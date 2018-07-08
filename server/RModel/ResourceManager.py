class ResourceManager:

    def __init__(self):
        self.db_connection = None

    def process_request(self, request):
        if request['REQ-TYPE'] == 'POST':
            if request['TARGET'][0] == 'g':
                pass # TODO check that user in group
            
        else: