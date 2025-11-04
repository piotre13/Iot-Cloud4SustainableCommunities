# app.py
import json, threading, os, shutil, cherrypy

# ---------- Shared store ----------
class CatalogStore:
    def __init__(self, path="catalog.json"):
        self.path = path
        self.lock = threading.RLock()
        self.data = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.data = json.load(f)

    def save(self):
        with self.lock:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            shutil.move(tmp, self.path)

# ---------- Services (REST) ----------
class ItemsAPI:
    exposed = True
    def __init__(self, store: CatalogStore):
        self.store = store

    # GET /api/items  or  GET /api/items/<id>
    def GET(self, item_id=None):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        with self.store.lock:
            items = self.store.data.setdefault("items", [])
            if item_id is None:
                return json.dumps(items)
            for it in items:
                if str(it.get("id")) == str(item_id):
                    return json.dumps(it)
        raise cherrypy.HTTPError(404, "Not found")

    # POST /api/items     (JSON body with {"id": ..., ...})
    def POST(self):
        body = cherrypy.request.body.read() or b"{}"
        try:
            obj = json.loads(body)
        except Exception:
            raise cherrypy.HTTPError(400, "Invalid JSON")
        if "id" not in obj:
            raise cherrypy.HTTPError(400, "Missing 'id'")
        with self.store.lock:
            items = self.store.data.setdefault("items", [])
            for i, it in enumerate(items):
                if str(it.get("id")) == str(obj["id"]):
                    items[i] = obj
                    break
            else:
                items.append(obj)
            self.store.save()
        cherrypy.response.status = 201
        return json.dumps({"status": "ok"})

class CategoriesAPI:
    exposed = True
    def __init__(self, store: CatalogStore):
        self.store = store

    def GET(self, category_id=None):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        with self.store.lock:
            cats = self.store.data.setdefault("categories", [])
            if category_id is None:
                return json.dumps(cats)
            for c in cats:
                if str(c.get("id")) == str(category_id):
                    return json.dumps(c)
        raise cherrypy.HTTPError(404, "Not found")

    def POST(self):
        body = cherrypy.request.body.read() or b"{}"
        try:
            obj = json.loads(body)
        except Exception:
            raise cherrypy.HTTPError(400, "Invalid JSON")
        if "id" not in obj:
            raise cherrypy.HTTPError(400, "Missing 'id'")
        with self.store.lock:
            cats = self.store.data.setdefault("categories", [])
            for i, c in enumerate(cats):
                if str(c.get("id")) == str(obj["id"]):
                    cats[i] = obj
                    break
            else:
                cats.append(obj)
            self.store.save()
        cherrypy.response.status = 201
        return json.dumps({"status": "ok"})

# Optional: a simple admin page (HTML) at a different mount
class AdminPage:
    exposed = True
    def __init__(self, store: CatalogStore):
        self.store = store
    def GET(self):
        with self.store.lock:
            items = len(self.store.data.get("items", []))
            cats = len(self.store.data.get("categories", []))
        return f"<h1>Catalog Admin</h1><p>Items: {items} | Categories: {cats}</p>"

def run(host="0.0.0.0", port=8080, data_path="catalog.json"):
    store = CatalogStore(data_path)

    # Per-mount configs: use MethodDispatcher at each service root
    rest_conf = {
        '/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()},
    }

    # Mount each service at a distinct endpoint
    cherrypy.tree.mount(ItemsAPI(store),      '/api/items',      config=rest_conf)
    cherrypy.tree.mount(CategoriesAPI(store), '/api/categories', config=rest_conf)

    # Mount a separate (non-REST) admin endpoint
    cherrypy.tree.mount(AdminPage(store), '/admin', config={'/': {}})

    # Optional: serve static files at /static
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    cherrypy.tree.mount(None, '/static', {
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': static_dir
        }
    })

    # Global server config
    cherrypy.config.update({
        'server.socket_host': host,
        'server.socket_port': port,
        'tools.encode.on': True,
        'tools.encode.encoding': 'utf-8',
        'environment': 'production',
    })

    # Start the engine
    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == '__main__':
    run()
