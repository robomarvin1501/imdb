import sys, os


class IMDB:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

        self.message = "Please select an option:\n1) Query by movies\n2) Query by actor\n3) Insert a new movie\n4) Save and Exit\n5) Exit\n\n"

        # Dictionary mapping movies to actors
        self.movie_to_actors = dict()
        # Set to keep track of all actors
        self.actors = set()
        self.actors_to_movies = dict()

        self.pre_processing()

        self.main()

    def main(self):
        user_option = ""
        while True:
            user_option = input(self.message)
            if user_option == '1':
                self.query_by_movies()
            elif user_option == '2':
                user_input = input("Name of actor: ")
                self.query_by_actors(user_input)
            elif user_option == '3':
                self.add_or_update_movie()
            elif user_option == '4':
                self.save_and_exit()
            elif user_option == '5':
                sys.exit()

    def pre_processing(self):
        """
        Extracts all of the data from the input file, and puts it into the relevant dictionaries for access
        """
        print('Starting pre processing...', end=' ')
        with open(self.input_file, 'r') as f:
            unparsed_data = f.read()

        lines = [self.parse_line(line) for line in unparsed_data.split('\n')]

        # Create dictionary mapping names of actors to movie titles
        self.actors_to_movies = {line[0]: set(line[1:]) for line in lines}

        # Populate self.movie_to_actors
        for actor in self.actors_to_movies.keys():
            self.actors.add(actor)
            for movie in self.actors_to_movies[actor]:
                if movie not in self.movie_to_actors:
                    self.movie_to_actors[movie] = {actor}
                else:
                    self.movie_to_actors[movie].add(actor)

        print('Done')
        # print(self.actors_to_movies)

    def query_by_movies(self):
        """
        Takes two names of movies, and an operator from set notation, and returns set1 blob set2
        """
        user_input = self.parse_line(input("Please select two movies and an operator(&,|,^) separated with ','\n"))
        if len(user_input) != 3:
            self.data_missing("incorrect_input")
            return

        movie_title_0, movie_title_1, operand = user_input
        # Checks that the movies are in the database by initialising the sets of actors
        try:
            actors_0 = self.movie_to_actors[movie_title_0]
            actors_1 = self.movie_to_actors[movie_title_1]
        except KeyError:
            print("One of the movies is not in our database")
            return

        if operand != '&' and operand != '|' and operand != '^':
            self.data_missing("incorrect_operand")
            return

        exec(f"self.pretty_print_sets(actors_0 {operand} actors_1)")

    def query_by_actors(self, actor):
        """
        Prints every costar of a given actor
        :param actor: str
        :return: None
        """
        # If the actor is not in the database, return early and print the error
        if actor not in self.actors:
            self.data_missing("actors")
            return
        every_costar = set()
        # Find every movie in which the actor appears, and add all the members of that cast to a set
        for movie in self.movie_to_actors.keys():
            if actor in self.movie_to_actors[movie]:
                every_costar |= self.movie_to_actors[movie]

        # Removes the actor so that he is not printed as well
        every_costar.remove(actor)

        self.pretty_print_sets(every_costar)

    def add_or_update_movie(self):
        """
        Adds a movie and all its actors to the database, or updates a movie in the database with new actors
        :return:
        """
        movie_data = self.parse_line(input("Style: Name of movie, Actor 1, Actor 2... \n"))
        if len(movie_data[1:]) == 0:
            self.data_missing("insufficient_data")
        if movie_data[0] in self.movie_to_actors.keys():
            # Updating existing data
            self.movie_to_actors[movie_data[0]] |= set(movie_data[1:])
        else:
            # Creates where there was non existent data
            self.movie_to_actors[movie_data[0]] = set(movie_data[1:])

        self.add_data_in_file_format(movie_data)

    def add_data_in_file_format(self, movie_data):
        """
        Adds data to the databases actors and actors_to_movies, which is kept in the file format for compatability
        :param movie_data: str "Movie_title, actor0, actor1, actor2...
        :return: None
        """
        actors = set(movie_data[1:])
        movie_title = movie_data[0]

        for actor in actors:
            if actor not in self.actors:
                self.actors.add(actor)
                self.actors_to_movies[actor] = {movie_title}
            else:
                self.actors_to_movies[actor].add(movie_title)

    def save_and_exit(self):
        """
        Write self.actors_to_movies to the output file
        :return:
        """
        output_data = ""
        for actor in sorted(self.actors_to_movies.keys()):
            output_data += actor + ', ' + ', '.join(sorted(list(self.actors_to_movies[actor])))
            output_data += '\n'

        with open(self.output_file, 'w') as f:
            f.write(output_data)

        sys.exit()

    @staticmethod
    def pretty_print_sets(the_set):
        """
        Prints sets in a pretty manner that does not include brackets or commas, and deals with empty sets
        :param the_set: Set
        :return: None
        """
        the_set = list(the_set)
        if the_set == {}:
            print("There are no actors in this group")
        else:
            for elem in the_set:
                if elem == the_set[-1]:
                    print(elem, end='\n\n')
                else:
                    print(elem, end=', ')

    @staticmethod
    def parse_line(line):
        """
        Takes a line and returns it as a list of words without spaces
        :param line: str
        :return: List[str]
        """
        return [word.strip() for word in line.split(',')]

    @staticmethod
    def data_missing(what_threw_the_error):
        """
        :param what_threw_the_error: str
        :return: None
        """
        if what_threw_the_error == "actors":
            print("There are no actors in this group")
        elif what_threw_the_error == "insufficient_data":
            print("You did not put in any actors")
        elif what_threw_the_error == "incorrect_input":
            print("Your input is wrong, please check you have the right number of values")
        elif what_threw_the_error == "incorrect_operand":
            print("Your operator does not exist as an option")


if __name__ == '__main__':
    imdb = IMDB(sys.argv[1], sys.argv[2])
