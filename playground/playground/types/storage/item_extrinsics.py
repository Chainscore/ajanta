class ItemExtrinsics:
    def __init__(self, db):
        self.db = db

    def get_all(self, package):
        # Return a list of extrinsics for each item in the package
        # Assuming package.items is a list of WorkItems
        # Each WorkItem has an extrinsic field which is a list of bytes
        return [item.extrinsic for item in package.items]
