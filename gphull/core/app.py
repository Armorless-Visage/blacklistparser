def address_action(add=False, remove=False):
    pass

def action_source_add(self):
    if self.args.timeout is None:
        raise ArgumentError('--timeout <s> must be specified')
    if self.args.format is None:
        raise ArgumentError
    # attempt to add source url to db
    Database.Utilities.add_source_url(
            self.db,
            self.args.add,
            self.args.format,
            self.args.timeout)
    self.db.db_conn.commit()     
  
def action_source_remove(self):
    # attempt to remove source url from db
    Database.Utilities.delete_source_url(
        self.db,
        self.args.remove)
    self.db.db_conn.commit()

def action_update(self):
    pass
def output_action():
    pass
def source_action():
    pass
