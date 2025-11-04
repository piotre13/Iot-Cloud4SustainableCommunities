


if __name__ == '__main__':
	conf = {
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on': True
		}
	}
	#cherrypy.quickstart(Webservice2(),'/string', conf)
	#cherrypy.tree.mount(Webservice2(), '/string', conf)
	cherrypy.tree.mount(Webservice3(), '/json', conf)
	cherrypy.engine.start()
	cherrypy.engine.block()