import time
import math


class track_generator:
    def __init__(self) -> None:
        
        #  Infomation from https://woodenrailway.info/track/brio-track-guide
        self.parts = {
            "A1": {"count": 2, "dir": 0.0, "mag": 108},
            "A2": {"count": 6, "dir": 0.0, "mag": 54},
            "A": {"count": 4, "dir": 0.0, "mag": 144},
            "D": {"count": 7, "dir": 0.0, "mag": 220},
            "E": {"count": 10 "dir": 45.0, "mag": 153},
            "E1": {"count": 2 "dir": 45.0, "mag": 72},
        }
        self.parts_bin = self.parts_to_bin(self.parts)
        self.variations = []
        self.variations_tested = 0
        self.complete_tracks = {}

    def parts_to_bin(self, parts: dict) -> list:
        """
        Takes a dictionary structure and returns a list of parts from the count
        value in the dict
        """
        p_bin = []
        for key in parts.keys():
            p_bin = p_bin + ([key] * parts[key]["count"])
        return p_bin

    def place_track_section(
        self, current_track: list, depth: int, locations: list, direction: float
    ) -> None:
        """
        Takes the current track and adds another peice then calls
        its self to recursivaly until there are no peices of track left
        If a type of track section has been used already it will not be used
        again
        """
        usable_track = self.parts_bin.copy()
        [usable_track.remove(x) for x in current_track]
        type_of_section_tested = []
        location = locations[len(locations) - 1]
        for track_length in range(0, len(usable_track)):
            if usable_track[track_length] not in type_of_section_tested:
                #  Add the track peice
                working_track = current_track.copy()
                working_track.append(usable_track[track_length])
                #  Calculate the new direction for both + and -
                if self.parts[usable_track[track_length]]["dir"] == 0.0:
                    directions = [0.0]
                else:
                    directions = [
                        self.parts[usable_track[track_length]]["dir"],
                        (self.parts[usable_track[track_length]]["dir"] * -1),
                    ]
                for angle in directions:
                    new_direction = direction + angle
                    if new_direction >= 360:
                        new_direction = new_direction - 360
                    #  Calculate the new end coordinate
                    x = location[0] + round(
                        (
                            math.cos(math.radians(new_direction))
                            * self.parts[usable_track[track_length]]["mag"]
                        ),
                        4,
                    )
                    y = location[1] + round(
                        (
                            math.sin(math.radians(new_direction))
                            * self.parts[usable_track[track_length]]["mag"]
                        ),
                        4,
                    )
                    new_location = locations.copy()
                    new_location.append([x, y])
                    self.variations_tested += 1
                    self.variations.append(working_track)
                    self.variations.append(working_track.reverse())
                    type_of_section_tested.append(usable_track[track_length])
                    if (abs(x) < 0.5) and (abs(y) < 0.5) and (abs(new_direction) < 1):
                        #  Finished track save
                        self.save_complete_track(working_track, new_location)
                    elif self.not_enough_track_to_return(x, y, usable_track):
                        #  Not enough track to return remove this peice and try again
                        continue
                    else:
                        #  Add next part
                        self.place_track_section(
                            working_track, (depth + 1), new_location, new_direction
                        )

    def save_complete_track(self, working_track: list, new_location: list) -> None:
        """
        Used to store circular tracks to a dictionary
        """
        self.complete_tracks["".join(working_track)] = {}
        x_points = []
        y_points = []
        for i in range(0, len(new_location)):
            x_points.append(new_location[i][0])
            y_points.append(new_location[i][1])
        self.complete_tracks["".join(working_track)]["x"] = x_points
        self.complete_tracks["".join(working_track)]["y"] = y_points
        self.complete_tracks["".join(working_track)]["track"] = working_track

    def not_enough_track_to_return(
        self, x: float, y: float, usable_track: list
    ) -> bool:
        """
        Returns true if there is not enough track to return to [0,0]
        """
        distance = math.sqrt(x**2 + y**2)
        remaining_track = 0.0
        for track_length in range(0, len(usable_track)):
            remaining_track = remaining_track + self.parts[usable_track[track_length]]["mag"]
        return (remaining_track <  distance)

    def build_track(self) -> None:
        """
        Called to initalise, build and save the tracks to file
        """
        start = time.time()
        print("Building track from peices: " + str(self.parts_bin))
        self.place_track_section([], 0, [[0.0, 0.0]], 0.0)
        time_taken = int(time.time() - start)
        print(
            "Found "
            + str(len(self.complete_tracks))
            + " tracks in "
            + str(time_taken)
            + " seconds having tested "
            + str(self.variations_tested)
            + " possabilities"
        )
        print("======================")
        with open("end_points.csv", "w") as file:
            for circuit in self.complete_tracks.keys():
                file.write(circuit + "\n")
                for i in range(0, len(self.complete_tracks[circuit]["x"]) - 1):
                    file.write(
                        self.complete_tracks[circuit]["track"][i]
                        + ", "
                        + str(int(self.complete_tracks[circuit]["x"][i]))
                        + ", "
                        + str(int(self.complete_tracks[circuit]["y"][i]))
                        + "\n"
                    )
                file.write("\n")
                print(circuit)


def main():
    track_gen = track_generator()
    track_gen.build_track()


if __name__ == "__main__":
    main()
