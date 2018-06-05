def first(iterable, condition = lambda x: True):
    for i in iterable:
        if condition(i):
            return i 

class KnownLocation:
    """Contains information such as name and 2D bounding box for a known location on the Dugged server."""
    @staticmethod
    def parse(values):
        dimension, location_name, x1, z1, x2, z2 = values

        # Skip locations with incomplete coords
        if x1 != 0 and z1 != 0 and x2 != 0 and z2 != 0:
            min_x = x1 if x1 < x2 else x2
            min_z = z1 if z1 < z2 else z2
            max_x = x2 if x2 > x1 else x1
            max_z = z2 if z2 > z1 else z1
            
            return KnownLocation(dimension, location_name, min_x, min_z, max_x, max_z)
        return None

    def __init__(self, dimension, location_name, min_x, min_z, max_x, max_z):
        self.dimension = dimension
        self.location_name = location_name
        self.min_x = min_x
        self.min_z = min_z
        self.max_x = max_x
        self.max_z = max_z

    def is_contained(self, x, z):
        # Determine whether the point is contained in the locations 2D bounding box
        return self.min_x <= x <= self.max_x and self.min_z <= z <= self.max_z
