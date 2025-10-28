

class Controller:
    def __init__(self, TH, rooms):
        self.threshold = TH
        self.rooms = rooms

    def control(self, sensed_data):
        for s_id , val in sensed_data.items():
            if val < self.threshold:

                
                
                pass
            else:
                pass


