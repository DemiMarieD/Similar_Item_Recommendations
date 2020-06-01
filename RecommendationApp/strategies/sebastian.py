import pickle
from pathlib import Path
from PIL import Image
from PIL import ImageStat
import requests
from io import BytesIO
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def calculate_luminance(r, g, b):
    return (0.299 * r + 0.587 * g + 0.114 * b)

# Calculate the average image brightness according to paper on p.11
def calculate_average_image_brightness(image):
    try:
        poster_stat = ImageStat.Stat(image)
        image_is_greyscale = False
        if len(image.getbands()) == 1:
            # If the image has only one band, it is a greyscale image
            image_is_greyscale = True

        if image_is_greyscale:
            intensity = poster_stat.mean
            avg_brightness = intensity[0]
        else:
            # Calculate the average RGB values for the image
            r, g, b = poster_stat.mean
            avg_brightness = calculate_luminance(r, g, b)
        return avg_brightness
    except:
        print("Error while trying to calculate the brightness for image.")
        return None

# Calculate the average image contrast according to paper on p.11
def calculate_average_image_contrast(image):
    try:
        poster_stat = ImageStat.Stat(image)
        image_is_greyscale = False
        if len(image.getbands()) == 1:
            # If the image has only one band, it is a greyscale image
            image_is_greyscale = True

        if image_is_greyscale:
            intensity = poster_stat.mean
            avg_intensity = intensity[0]
        else:
            r, g, b = poster_stat.mean
            avg_intensity = calculate_luminance(r, g, b)

        sum_contrast = 0
        for x in range(image.width):
            for y in range(image.height):
                if image_is_greyscale:
                    pixel_luminance = image.getpixel((x, y))
                else:
                    r, g, b = image.getpixel((x, y))
                    pixel_luminance = calculate_luminance(r, g, b)
                sum_contrast += pixel_luminance - avg_intensity

        avg_contrast = sum_contrast / (image.width * image.height)
        return avg_contrast
    except:
        print("Error while trying to calculate the contrast for image.")
        return None

# Returns the colour histogram of an image
def get_image_similarity_histogram(image):
    try:
        histogram = image.histogram()
        # 256*3 => RGB channels are concatenated
        # Length is the same for grayscale images
        if len(histogram) != 256*3:
            return None
        return np.asarray(histogram)
    except:
        print("Error while trying to get colour histogram for image.")
        return None

# Use Manhattan distance for similarity calculation.
# In the paper it is used for multiple low-level feature comparisons,
# e.g. brightness, sharpness, colourfulness, contrast, ...
def calculate_image_similarity(value_image_1, value_image_2):
    return 1 - abs(value_image_1 - value_image_2)

# The similarity method uses the cosine similarity between tow vectors
def calculate_image_similarity_histogram(histogram_1, histogram_2):
    similarity = cosine_similarity([histogram_1], [histogram_2])
    return similarity

# Returns the image as Pillow image if available, otherwise None
def get_image_from_url(url):
    # https://stackoverflow.com/questions/7391945/how-do-i-read-image-data-from-a-url-in-python
    try:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        return image
    except:
        print("Error while trying to open the image from URL: ", url)
        return None


def get_top_5(relevant_movies, descending):
    # get top 5 - Similarities are in a range of [-255, 1], where 1 means similar
    sorted_list = sorted(relevant_movies, key=lambda tup: tup[1], reverse=descending)

    if len(sorted_list) > 5:
        sorted_list = sorted_list[:5]

    similar_movies = []  # value:  title
    for tuple in sorted_list:
        similar_movies.append(int(tuple[0]))

    return similar_movies


class Image_Based_Recommender:

    def __init__(self, data):
        self.serialized_movieposter_data_path = 'RecommendationApp/data/serialized/serialized_movieposter_data.obj'
        self.movieposter_metadata = {}

        if Path(self.serialized_movieposter_data_path).is_file():
            self.load_serialized_movieposter_data()
        else:
            # Calculate relevant image metadata values for each poster
            for m_id, value in data.items():
                self.movieposter_metadata[m_id] = {}
                if value['poster'] is not None:
                    poster = get_image_from_url(value['poster'])
                    self.movieposter_metadata[m_id]['avg_brightness'] = calculate_average_image_brightness(poster)
                    self.movieposter_metadata[m_id]['avg_contrast'] = calculate_average_image_contrast(poster)
                    self.movieposter_metadata[m_id]['colour_histogram'] = get_image_similarity_histogram(poster)
                else:
                    # TODO: Maybe better -1?
                    self.movieposter_metadata[m_id]['avg_brightness'] = None
                    self.movieposter_metadata[m_id]['avg_contrast'] = None
                    self.movieposter_metadata[m_id]['colour_histogram'] = None

            self.serialize_movieposter_data_file()


    def using_poster_brightness(self, data, movie_id):
        # If there is no poster for the given movie, skip image-based recommendation
        if data[movie_id]['poster'] is None:
            return None

        relevant_movies = []  # list of tuples: id, similarity
        target_movie_brightness = self.movieposter_metadata[movie_id]['avg_brightness']
        for m_id, value in self.movieposter_metadata.items():
            if m_id != movie_id and value['avg_brightness'] is not None:
                relevant_movies.append(
                    (m_id, calculate_image_similarity(target_movie_brightness, value['avg_brightness'])))

        result = get_top_5(relevant_movies, True)
        return result


    def using_poster_contrast(self, data, movie_id):
        # If there is no poster for the given movie, skip image-based recommendation
        if data[movie_id]['poster'] is None:
            return None

        relevant_movies = []  # list of tuples: id, similarity
        target_movie_contrast = self.movieposter_metadata[movie_id]['avg_contrast']
        for m_id, value in self.movieposter_metadata.items():
            if m_id != movie_id and value['avg_contrast'] is not None:
                relevant_movies.append(
                    (m_id, calculate_image_similarity(target_movie_contrast, value['avg_contrast'])))

        result = get_top_5(relevant_movies, True)
        return result

    # Uses similarity of histograms
    def using_poster_colour_histogram(self, data, movie_id):
        # If there is no poster for the given movie, skip image-based recommendation
        if data[movie_id]['poster'] is None:
            return None

        relevant_movies = []  # list of tuples: id, similarity
        target_movie_histogram = self.movieposter_metadata[movie_id]['colour_histogram']
        for m_id, value in data.items():
            poster_metadata = self.movieposter_metadata[m_id]
            if m_id != movie_id and poster_metadata['colour_histogram'] is not None:
                relevant_movies.append(
                    (m_id, calculate_image_similarity_histogram(target_movie_histogram, poster_metadata['colour_histogram'])))

        result = get_top_5(relevant_movies, True)
        return result

    # Use colour similarity plus genre
    def using_poster_colour_histogram_and_genre(self, data, movie_id):
        # If there is no poster for the given movie, skip image-based recommendation
        if data[movie_id]['poster'] is None:
            return None

        target_genres = data[movie_id]['genres']  # list of string
        relevant_movies = {}  # subset of movie data, only containing relevant movies (with genre overlap)
        relevant_movies[movie_id] = data[movie_id] # Add target movie
        for m_id, value in data.items():
            if m_id != movie_id:
                genres = data[m_id]['genres']
                if genres is not None:
                    intersection_set = set.intersection(set(target_genres), set(genres))
                    # The genres should intersect in at least 80%
                    if len(intersection_set) >= len(target_genres) * 0.8:
                        relevant_movies[m_id] = data[m_id]

        return self.using_poster_colour_histogram(relevant_movies, movie_id)


    # Loads the serialized movieposter_metadata object
    def load_serialized_movieposter_data(self):
        with open(self.serialized_movieposter_data_path, 'rb') as serialized_file:
            serialized_movieposter_data: dict = pickle.load(serialized_file)
        for key, value in serialized_movieposter_data.items():
            self.movieposter_metadata[key] = value

    # Dumps the movieposter_metadata object as serialized file
    def serialize_movieposter_data_file(self):
        with open(self.serialized_movieposter_data_path, 'wb') as serialized_file:
            pickle.dump(self.movieposter_metadata, serialized_file, pickle.HIGHEST_PROTOCOL)

