import matplotlib.pyplot as plt
import matplotlib.patches as patches


# https://opus4.kobv.de/opus4-zib/frontdoor/deliver/index/docId/177/file/SC-95-11.pdf
# M Dellnitz, A Hohmann
# A subdivision algorithm for the computation of unstable manifolds and global attractors
class Subdivision:
    boxes_activeness = None
    borders = None
    depth = -1
    num_boxes_per_dimension = -1
    num_test_points_per_dimension = 5
    num_all_test_points = -1
    system = None

    def __init__(self, system, depth_start, borders, all_active=True):
        self.system = system
        self.depth = depth_start
        self.borders = borders
        dimension = len(borders)
        self.num_boxes_per_dimension = 1
        for i in range(depth_start):
            self.num_boxes_per_dimension *= 2
        num_boxes = 1
        self.num_all_test_points = 1
        for i in range(dimension):
            num_boxes *= self.num_boxes_per_dimension
            self.num_all_test_points *= self.num_test_points_per_dimension

        self.boxes_activeness = [all_active for i in range(num_boxes)]

    @staticmethod
    def do_subdivision(system, borders, up_to_depth):
        ret = Subdivision(system, 3, borders)

        while ret.depth != up_to_depth:
            ret = ret.subdivide()

        return ret

    def plot(self):
        print("Plotting started")

        if self.system.dimension == 2:
            current_gca = plt.gca()
            for i in range(len(self.boxes_activeness)):
                if self.boxes_activeness[i]:
                    position = self.get_position(i, self.num_boxes_per_dimension)
                    box_borders = self.get_box_borders(position)
                    current_gca.add_patch(
                        patches.Rectangle((box_borders[0][0], box_borders[1][0]),
                                          box_borders[0][1] - box_borders[0][0],
                                          box_borders[1][1] - box_borders[1][0],
                                          facecolor="red",
                                          alpha=0.5))
        print("Plotting ended")

    def subdivide(self):
        print("Subdivision started ", self.depth + 1)
        ret = Subdivision(self.system, self.depth + 1, self.borders, False)

        for i in range(len(self.boxes_activeness)):
            if self.boxes_activeness[i]:
                position = self.get_position(i, self.num_boxes_per_dimension)
                box_borders = self.get_box_borders(position)
                for j in range(self.num_all_test_points):
                    position_within_box = self.get_position(j, self.num_test_points_per_dimension)
                    test_point = self.get_point_in_box(
                        box_borders, position_within_box, self.num_test_points_per_dimension)
                    mapped_test_point = self.system.map_point(test_point)
                    ret.active_box_with_point(mapped_test_point)
        print("Subdivision ended ", ret.depth)
        return ret

    def active_box_with_point(self, point):
        position = [0 for i in range(len(self.borders))]
        for i in range(len(self.borders)):
            if point[i] < self.borders[i][0] or point[i] > self.borders[i][1]:
                return
            position[i] = int((point[i] - self.borders[i][0]) * self.num_boxes_per_dimension
                              / (self.borders[i][1] - self.borders[i][0]))
            if position[i] < 0:
                position[i] = 0
            if position[i] >= self.num_boxes_per_dimension:
                position[i] = self.num_boxes_per_dimension -1

        self.boxes_activeness[self.get_index(position)] = True

    def get_point_in_box(self, borders, position, points_per_dimension):
        ret = [0 for i in range(len(borders))]
        for i in range(len(borders)):
            ret[i] = borders[i][0] + (borders[i][1] - borders[i][0]) \
                                     * (position[i] + 1) / (points_per_dimension + 1)

        return ret

    def get_box_borders(self, position):
        ret = [[] for i in range(len(position))]
        for i in range(len(position)):
            tmp = [0,0]
            tmp[0] = self.borders[i][0] + (self.borders[i][1] - self.borders[i][0]) \
                                          * position[i] / self.num_boxes_per_dimension
            tmp[1] = self.borders[i][0] + (self.borders[i][1] - self.borders[i][0]) \
                                          * (position[i] + 1) / self.num_boxes_per_dimension
            ret[i] = tmp

        return ret

    def get_index(self, position):
        ret = 0
        for i in range(len(self.borders)-1,-1,-1):
            ret *= self.num_boxes_per_dimension
            ret += position[i]

        return ret

    def get_position(self, index, num_per_dimension):
        ret = [0 for i in range(len(self.borders))]
        for i in range(len(self.borders)):
            ret[i] = index % num_per_dimension
            index //= num_per_dimension

        return ret