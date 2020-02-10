from tendo import singleton

import configparser
import os
import re
import time
from pprint import pprint

import common.db_utils as db_utils
import common.playlist_utils as playlist_utils
import common.tv_maze as tv_maze

# Throw an exception if this script is already running
me = singleton.SingleInstance()

db_utils.initialize_db()


# Given a show name, this function will populate the SQLite DB with all of the episode information
# for that show
def populate_tv_maze_episode_info(show_name):
    series_id = db_utils.get_series_id(show_name)

    episodes_api_response = tv_maze.show_episode_list(series_id)
    for curr in episodes_api_response:
        episode_subtitle = 'S' + str(curr['season']) + 'E' + str(curr['number'])
        if not (curr['summary'] is None):
            description = curr['summary'].replace('<p>', '').replace('</p>', '')
        else:
            description = ''

        db_utils.save_tv_maze_episode(series_id, curr['season'], curr['number'], curr['name'],
                                      episode_subtitle, description)
    db_utils.populate_series_absolute_order(series_id)


def populate_episode_lengths(directory_full_path):
    series_directory_name = os.path.basename(directory_full_path)
    series_id = db_utils.get_series_id(series_directory_name)
    file_list = playlist_utils.list_files_with_path(directory_full_path)
    for file_full_path in file_list:
        file_name = os.path.basename(file_full_path)
        length = playlist_utils.get_video_length(file_full_path)
        season, episode = playlist_utils.parse_season_episode(os.path.basename(file_name))
        db_utils.save_local_episode(series_id, season, episode, length, file_full_path)


def populate_all_episode_info(directory_full_path):
    directory_name = os.path.basename(directory_full_path)
    if not db_utils.is_series_metadata_loaded(directory_name):
        populate_tv_maze_episode_info(directory_name)
        populate_episode_lengths(directory_full_path)
        db_utils.update_series_last_updated_time(directory_name)


def start_channel(channel_name, order, channel_series_id):
    channel_result = db_utils.get_channel(channel_name)
    if channel_result is None:
        db_utils.save_channel(channel_name, order, channel_series_id)
        channel_result = {
            'channel': channel_name,
            'playbackOrder': order,
            'seriesID': channel_series_id,
            'nextEpisode': 0
        }
    result = db_utils.get_episodes_in_order(channel_result['seriesID'], channel_result['nextEpisode'])
    print(result)


config = configparser.ConfigParser()
config.read('config.ini')

for channel in config.sections():
    directory = config.get(channel, "directory")
    playback_order = config.get(channel, "order")

    directory_series_id = db_utils.get_series_id(os.path.basename(directory))

    populate_all_episode_info(directory)
    start_channel(channel, playback_order, directory_series_id)

