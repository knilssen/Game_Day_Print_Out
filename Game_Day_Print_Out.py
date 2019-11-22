#
#
#
#   in order to run we need:
#           pip install requests
#           pip install html5lib
#           pip install bs4
#           pip install unidecode
#
#
#
#
#
#
#
#   Possible do a by league in our game information as well?
#   so it would look like:
#       [ sport ]             ex:          [ football ]
#
#           |
#
#       [ league ]                         [ ncaa ]
#
#           |
#
#       [ games ]                           [ matchup data]
#
#
#
#   This way we can print this out easier by sport, by league so like ncaa and nfl would be separate and then by time
#
#
#
#
#

import sys
import requests
import pytz
import re
import unidecode
import csv
from openpyxl import Workbook
from openpyxl.styles import Alignment
from pytz import timezone
from datetime import datetime
from bs4 import BeautifulSoup
from datetime import date

list_of_sports_we_dont_want_or_need = ["combat sports", "volleyball"]
list_of_sports_without_home_and_away =  ["golf", "tennis", "racing", "Racing", "Golf", "Tennis"]

streaming_channels = ['espn3', 'espn+']
channels_not_on_comcast = ['accn']
directv_channel_broadcasters = {'KCPQ':'fox', 'KOMO':'abc', 'KIRO':'cbs', 'KING':'nbc'}
comcast_channel_broadcasters = {'kcpq':'fox', 'komo':'abc', 'kiro':'cbs', 'king':'nbc', 'rootnw':'root', 'cbss':'cbssn', 'nbsnw':'nbsn'}
comcast_channel_numbers = {'amc':  '67',
                           'abc':   '104',
                           'nbc':   '105',
                           'cbs':   '107',
                           'joetv': '110',
                           'fox':   '113',
                           'espn':  '173',
                           'espn2':  '174',
                           'nbsn':    '179',
                           'byu':  '232',
                           'espnu':  '400',
                           'cbssn':  '412',
                           'fs2':  '413',
                           'pacwa':  '430',
                           'foxde':  '602',
                           'fs1':   '620',
                           'espnu':  '621',
                           'golf': '625',
                           'nbcs': '626',
                           'root':  '627',
                           'pac12':  '628',
                           'tnns': '634',
                           'sec':   '638',
                           'fs1':   '620',
                           'tnt':  '662',
                           'tbs':  '664',
                           'usa':  '672'}

null_unicode = 'null'.decode('utf_8')


#
#
#
class Directv_address:
    def __init__(self, todays_date, zip_code):
        # Directv address variables
        self.schedule_filter_type = "1"
        self.scheudle_group_id = "0"
        self.start_date = todays_date
        self.zip_code = zip_code
        self.account_type = "20"
        self.package_filter_enabled = "False"
        self.team_highlight_enabled = "False"
        self.show_replays = "1"
        self.show_eastern_time = "False"
        self.display_mode = "2"
        self.grouping = "2"
        # self.season = "nfl"

        # Directv address pieces
        self.directv_address_beggining = "http://sports.directv.com/home.htm?"
        self.address_schedule_filter_type = "ScheduleFilterType="
        self.address_scheudle_group_id = "ScheduleGroupID="
        self.address_start_date = "StartDate="
        self.address_zip_code = "Zip="
        self.address_account_type = "AccountType="
        self.address_package_filter_enabled = "PackageFilterEnabled="
        self.address_team_highlight_enabled = "TeamHighlightEnabled="
        self.address_show_replays = "ShowReplays="
        self.address_show_eastern_time = "ShowEasternTime="
        self.address_display_mode = "DisplayMode="
        self.address_grouping = "Grouping="
        # self.address_season = "&Season="

    #
    #
    #
    def print_variables(self):
        print "\n"
        print "Directv address variables:"
        print "%s %s" % (self.address_schedule_filter_type, self.schedule_filter_type)
        print "%s %s" % (self.address_scheudle_group_id, self.scheudle_group_id)
        print "%s %s" % (self.address_start_date, self.start_date)
        print "%s %s" % (self.address_zip_code, self.zip_code)
        print "%s %s" % (self.address_account_type, self.account_type)
        print "%s %s" % (self.address_package_filter_enabled, self.package_filter_enabled)
        print "%s %s" % (self.address_team_highlight_enabled, self.team_highlight_enabled)
        print "%s %s" % (self.address_show_replays, self.show_replays)
        print "%s %s" % (self.address_show_eastern_time, self.show_eastern_time)
        print "%s %s" % (self.address_display_mode, self.display_mode)
        print "%s %s" % (self.address_grouping, self.grouping)
        print "\n"

    #
    #
    #
    def get_address(self):

        #
        directv_address_variables = "&".join([self.address_schedule_filter_type + self.schedule_filter_type,
                                            self.address_scheudle_group_id + self.scheudle_group_id,
                                            self.address_start_date + self.start_date,
                                            self.address_zip_code + self.zip_code,
                                            self.address_account_type + self.account_type,
                                            self.address_package_filter_enabled + self.package_filter_enabled,
                                            self.address_team_highlight_enabled + self.team_highlight_enabled,
                                            self.address_show_replays + self.show_replays,
                                            self.address_show_eastern_time + self.show_eastern_time,
                                            self.address_display_mode + self.display_mode,
                                            self.address_grouping + self.grouping])
        #
        directv_full_address = "".join([self.directv_address_beggining, directv_address_variables])

        return directv_full_address


class Game_info:
    def __init__(self, sport, league, first_team, second_team, home_team, time, broadcaster, directv_channel_info, comcast_channel_info):
        #
        # print (sport, league, first_team, second_team, home_team, time, broadcaster, directv_channel_info, comcast_channel_info)
        for x in range(0, len(broadcaster)):
            broadcaster[x] = str(unidecode.unidecode(broadcaster[x])).lower()


        self.sport = str(unidecode.unidecode(sport)).lower()
        self.league = str(unidecode.unidecode(league)).lower()
        self.first_team = str(unidecode.unidecode(first_team)).lower()
        self.second_team = str(unidecode.unidecode(second_team)).lower()
        self.home_team = str(unidecode.unidecode(home_team)).lower()
        self.time = time
        self.broadcaster = broadcaster
        self.directv_channel_number = directv_channel_info
        self.comcast_channel_number = comcast_channel_info

    def __str__(self):
        return "%s  %s  %s  %s  %s  %s  %s  %s" % (self.league, self.first_team, self.second_team, self.home_team, self.time, self.broadcaster, self.directv_channel_number, self.comcast_channel_number)

    def return_for_tsv_printing(self):
        return_list = []

        if self.home_team == "null":
            # We have no home team which means that we might not have a second team. Check if we do.
            if self.second_team != "null":
                # We have no home team but we still have two teams
                return_list = ['', self.league, self.first_team.title(), ' vs ', self.second_team.title(), self.time]

            else:
                # We have no home team and no second team
                return_list = ['', self.league, self.first_team.title(), '', '', self.time]

        else:
            # if we have a home team we also have a first and second team
            if self.first_team == self.home_team:
                return_list = ['', self.league, self.second_team.title(), ' at ', self.first_team.title(), self.time]
            else:
                return_list = ['', self.league, self.first_team.title(), ' at ', self.second_team.title(), self.time]

        # Now if we have directv channels lets add them
        if self.directv_channel_number != 'null':
            directv_channel_number_tsv_string = ''
            for broadcaster in self.broadcaster:
                if broadcaster in self.directv_channel_number:
                    # When we have multple channels for the same broadcasting name
                    for broadcasting_name_channels in self.directv_channel_number[broadcaster]:
                        directv_channel_number_tsv_string += (broadcaster.upper() + ': ' + broadcasting_name_channels['number'] + '  ')

                    # directv_channel_number_tsv_string += (broadcaster.upper() + ': ' + self.directv_channel_number[broadcaster]['number'] + '  ')

            return_list.append(directv_channel_number_tsv_string)
        else:
            return_list.append('')


        # Now if we have comcast channels lets add them
        if self.comcast_channel_number != 'null':
            comcast_channel_number_tsv_string = ''
            for broadcaster in self.broadcaster:
                if broadcaster in self.comcast_channel_number:
                    comcast_channel_number_tsv_string += (broadcaster.upper() + ': ' + self.comcast_channel_number[broadcaster]['number'] + '  ')

            return_list.append(comcast_channel_number_tsv_string)
        else:
            return_list.append('')

        # Now lets return our list
        return return_list


def directv_html_parsing(directv_url, todays_date):
    URL = directv_url
    raw_directv_html = requests.get(URL)

    directv_soup = BeautifulSoup(raw_directv_html.content, 'html5lib')

    # make a dictionary for what we find
    directv_dictionary = {}

    sport_table = directv_soup.findAll('div', attrs = {'class':'tableWrap tableLevel1'})

    for sport in sport_table:
        sport_name = sport.find('div', attrs = {'class':'tableTitle'}).text
        sport_name = (sport_name).split(sport.find('span', attrs = {'class':'dateWithinHeader'}).text)[0]
        sport_name = str(sport_name).lower()

        sport_list_of_games = []

        if sport_name not in list_of_sports_we_dont_want_or_need:

            # print "Found sport: ", sport_name

            for matchup in sport.findAll('div', attrs = {'class':'gameInfo'}):

                league = matchup.find('div', attrs = {'class':'sportLabel'}).text

                if sport_name in list_of_sports_without_home_and_away:
                    first_team = matchup.find('span', attrs = {'class':'eventTitle'}).text
                    second_team = null_unicode
                    home_team = null_unicode
                else:
                    teams = matchup.find('span', attrs = {'class':'eventTitle'}).text
                    if " at " in teams:
                        teams = teams.split(' at ')
                        # Home team is the second team becuase the format is [first team] AT [second team]. This means its being played at the second team
                        home_team = teams[1]
                    elif " vs " in teams:
                        teams = teams.split(' vs ')
                        home_team = null_unicode
                    elif " vs. " in teams:
                        teams = teams.split(' vs. ')
                        home_team = null_unicode
                    elif " en " in teams:
                        # Incase we have a spanish broadcast
                        teams = teams.split(' en ')
                        home_team = null_unicode
                    elif " v. " in teams:
                        # incase we have a spanish broadcast
                        teams = teams.split(' v. ')
                        home_team = null_unicode
                    else:
                        print "\n"
                        print "Error: cant split between home and away teams"
                        print "         option 1:   sport is not a teamed sport and is not inlcuded in list_of_sports_without_home_and_away"
                        print "         option 2:   this is a new home and away language that is different than [ at ] and [ vs ] and [ vs. ]"
                        print "         option 3:   sport is not a teamed sport or uses new language but is an undesired sport but is not inlcuded in list_of_sports_we_dont_want_or_need"
                        print "\n"
                        print "\n"
                        print "Error caused by teams:", teams
                        print "Quitting program...."
                        print "Error message sent to developer. Please contact developer if not fixed in timely matter or this error is repeated multiple days in a row"
                        print "\n"
                        sys.exit()

                    first_team = teams[0]
                    second_team = teams[1]


                time = matchup.find('span', attrs = {'class':'timeText'}).text
                time = datetime.strptime(time, '%I:%M %p')
                time = time.strftime("%I:%M %p")

                channel_rows = matchup.find('div', attrs = {'class':'channelRows'})

                channel_name_list = []
                channel_number_dictionary = {}

                for channel in channel_rows.findAll('div', attrs = {'class':'channelRow'}):

                    channel_number_dictionary_entry_form = {'number':'null', 'feed':'null', 'definiton':'standard'}

                    channel_name = (channel.find('span', attrs = {'class':'channelCallsign'}).text)
                    channel_name = str(unidecode.unidecode(channel_name)).lower()
                    if channel_name in directv_channel_broadcasters:
                        channel_name = directv_channel_broadcasters[channel_name]

                    channel_number_dictionary_entry_form['number'] = channel.find('span', attrs = {'class':'channelNumNew'}).text

                    channel_feed = channel.find('span', attrs = {'class':'infoTag feed'})
                    if channel_feed != None:
                        # for some reason Im not having any success with removeing the " (" from before the feed and ")" from after the feed for in this example with NHL matchups
                        channel_feed = channel_feed.text
                        channel_feed_2 = channel_feed.replace(" ()", "")
                        channel_number_dictionary_entry_form['feed'] = channel_feed_2

                    channel_definition = channel.find('span', attrs = {'class':'infoTag gray'})
                    if channel_definition != None:
                        channel_number_dictionary_entry_form['definiton'] = channel_definition.text


                    # Since for some reason directv shows sometimes the channel 'fox' to have the channel number 'FOX' instead of a number like 13 or 113, we should
                    # check if the channel number we found for the channel is actually a number. If its not, we should just discard this entry and for every instance found
                    # that this happens, the channel fox: 13 is still shown when we also have fox: FOX.

                    # We are using .isdigit() becuase we know the channel number has to be a positive whole integer that has no letters in it.
                    if channel_number_dictionary_entry_form['number'].isdigit():

                        # if channel_name is already in the list dont add it again. This happens when we have an NHL game where there are multiple NHL channels with the
                        # channel name of NHL
                        if channel_name not in channel_name_list:
                            channel_name_list.append(channel_name)

                        # If we have the same as above, same channel name but different numbers, add to the dictionary value as a list
                        if channel_name in channel_number_dictionary:
                            channel_number_dictionary[channel_name].append(channel_number_dictionary_entry_form)
                        else:
                            channel_number_dictionary[channel_name] = [channel_number_dictionary_entry_form]



                new_game = Game_info(sport_name.decode('utf_8'), league, first_team, second_team, home_team, time, channel_name_list, channel_number_dictionary, 'null')
                sport_list_of_games.append(new_game)

            directv_dictionary[sport_name] = sport_list_of_games

        else:
            # print "Found sport we dont want or need: ", sport_name
            continue

    return directv_dictionary






def espn_college_football_html_parsing(espn_college_football_url, todays_date, local_tz):
    URL = espn_college_football_url
    raw_espn_college_football_html = requests.get(URL)

    espn_college_football_soup = BeautifulSoup(raw_espn_college_football_html.content, 'html5lib')

    # make a dictionary for what we find
    espn_college_football_dictionary = {}

    # make the holder inside
    espn_list_of_games = []

    football_schedule_table = espn_college_football_soup.find('div', attrs = {'id':'schedule-page','class':'football'})
    football_schedule_table = football_schedule_table.find('div', attrs = {'id':'sched-container'})
    football_schedule_table = football_schedule_table.findChildren(recursive=False)

    collect_next_group_of_games = False

    for items in football_schedule_table:
        print "\n"

        if collect_next_group_of_games == False:
            if items.name == 'h2':
                # print items.text
                found_date = items.text + " " + date.today().strftime("%Y")
                found_date = datetime.strptime(found_date, '%A, %B %d %Y')
                # print found_date

                found_date = found_date.strftime("%m-%d-%Y")

                if found_date == todays_date:
                    collect_next_group_of_games = True
                    continue
                elif found_date < todays_date:
                    #continue on in the loop
                    # print "continue to find todays date"
                    continue
                else:
                    # found date is in the future, exit loop, either no games today or we have already found the games today
                    print "oh no we have passed our date.... This should have not happened! Something went wrong here"
                    break

        else:
            # do collection stuff and then exit the loop
            games = items.find('tbody')

            # print "Amount of games found for today:", len(games.findAll('tr'))

            for matchup in games.findAll('tr'):
                for matchup_data in matchup.findAll('td'):
                    if matchup_data.has_attr('class') and matchup_data['class'][0] == 'home':
                        # print matchup_data.find('a', attrs = {'class':'team-name'}).span.text
                        espn_matchup_home_team = matchup_data.find('a', attrs = {'class':'team-name'}).span.text
                        # print "should be our HOME team?"
                    elif matchup_data.has_attr('class') and matchup_data['class'][0] == '':
                        # print matchup_data.find('a', attrs = {'class':'team-name'}).span.text
                        espn_matchup_away_team = matchup_data.find('a', attrs = {'class':'team-name'}).span.text
                        # print "should be our away team?"
                    elif matchup_data.has_attr('data-behavior') and matchup_data['data-behavior'] == 'date_time':
                        found_dateTime = matchup_data['data-date']
                        found_dateTime = datetime.strptime(found_dateTime, '%Y-%m-%dT%H:%MZ')
                        found_dateTime = local_tz.localize(found_dateTime)
                        found_dateTime = found_dateTime.astimezone(timezone('US/Pacific'))
                        espn_matchup_time = found_dateTime.strftime("%I:%M %p")
                        # print found_dateTime.strftime("%I:%M %p")


                    elif matchup_data.has_attr('class') and matchup_data['class'][0] == 'network':
                        # print matchup_data
                        if matchup_data.text != "":
                            # print "we found matchup_data text:", matchup_data.text
                            espn_matchup_network = matchup_data.text
                        elif matchup_data.find('img'):
                            # print "We did not find matchup_data text. This means it must be a picture and we have to look in the pictures tags for the network info!"
                            # get the alt and the class tags
                            # if they match then we make that our network name
                            # easy
                            # print "alt:", matchup_data.img['alt']
                            # print "class:", matchup_data.img['class'][0]

                            if matchup_data.img['alt'] == matchup_data.img['class'][0]:
                                espn_matchup_network = matchup_data.img['class'][0]
                                # print "our alt and class for the network image are the same:", matchup_data.img['class'][0]

                        else:
                            # No network found. Game is not televised?
                            espn_matchup_network = null_unicode
                            # print "No network found. Game is not televised?"

                        # print "should be our network?"

                # print "\n"
                if espn_matchup_network != null_unicode:
                    new_game = Game_info('football'.decode('utf_8'), 'ncaa', espn_matchup_home_team, espn_matchup_away_team, espn_matchup_home_team, espn_matchup_time, [espn_matchup_network], 'null', 'null')
                    espn_list_of_games.append(new_game)
                    # print new_game, "\n"

        espn_college_football_dictionary['football'] = espn_list_of_games

        return espn_college_football_dictionary


def compare_add_directv_espn(directv_games, espn_college_football_games):
    # comapre the football games we found on espn to the football games we found on directv and then add the games that are only on comacast

    matches_found_list = []
    no_matches_found_list = []

    if len(espn_college_football_games['football']) != 0:
        for espn_football_matchup in espn_college_football_games['football']:
            same_game_found = False
            for directv_football_matchup in directv_games['football']:
                if directv_football_matchup.league == "ncaa":

                    if (directv_football_matchup.first_team == espn_football_matchup.first_team and directv_football_matchup.second_team == espn_football_matchup.second_team) or (directv_football_matchup.first_team == espn_football_matchup.second_team and directv_football_matchup.second_team == espn_football_matchup.first_team):
                        same_game_found = True
                        # print 'match found:', directv_football_matchup, espn_football_matchup
                        matches_found_list.append(espn_football_matchup)
                        break

                    # Now we have to check if espn and directv used different names for the teams.
                    # Example texas vs TCU
                    # One did TCU and the other is texas christian university
                    # To check for this. If one of the teams matches but the other doesnt, check the network for those games
                    # If the network matches up we will count it as a match
                    elif (directv_football_matchup.first_team == espn_football_matchup.first_team or directv_football_matchup.first_team == espn_football_matchup.second_team) or (directv_football_matchup.second_team == espn_football_matchup.first_team or directv_football_matchup.second_team == espn_football_matchup.second_team):
                        # print 'possible match found:', directv_football_matchup, espn_football_matchup
                        # print "\n possible matchup found, teams:", directv_football_matchup.first_team, directv_football_matchup.second_team
                        # print "broadcasters are:", directv_football_matchup.broadcaster, espn_football_matchup.broadcaster

                        # if  directv_football_matchup.broadcaster[0] == espn_football_matchup.broadcaster[0]:
                        if espn_football_matchup.broadcaster[0] in directv_football_matchup.broadcaster:
                            # print "possible match found, broadcasters line up"
                            # print "times are:", directv_football_matchup.time, espn_football_matchup.time
                            if directv_football_matchup.time == espn_football_matchup.time:
                                # print "matchup found, times line up as well!"

                                same_game_found = True
                                # print 'match found:', directv_football_matchup, espn_football_matchup
                                matches_found_list.append(espn_football_matchup)
                                break


            if same_game_found == False:
                # print "no match found for espn football matchup:", espn_football_matchup

                # If the reason why we can not find a match is becuase it is a streaming only chnanel,
                # then we dont need this games information and we can exclude it from our find
                if espn_football_matchup.broadcaster[0] not in streaming_channels and espn_football_matchup.broadcaster[0] not in channels_not_on_comcast:
                    # Try to add a comcast only channel number list for stuff like pac12 network so the channel number is already added at this step
                    if espn_football_matchup.broadcaster[0] in comcast_channel_numbers:
                        channel_number_dictionary = {}
                        channel_number_dictionary_entry_form = {'number':'null', 'feed':'null', 'definiton':'standard'}
                        channel_number_dictionary_entry_form['number'] = comcast_channel_numbers[espn_football_matchup.broadcaster[0]]
                        channel_number_dictionary_entry_form['definiton'] = "hd"
                        channel_number_dictionary[espn_football_matchup.broadcaster[0]] = channel_number_dictionary_entry_form
                        espn_football_matchup.comcast_channel_number = channel_number_dictionary

                        no_matches_found_list.append(espn_football_matchup)

                    else:
                        no_matches_found_list.append(espn_football_matchup)


        # Add not found games that are not streaming channles to our found games
        for no_match_found in no_matches_found_list:
            directv_games['football'].append(no_match_found)
            # print no_match_found

        return directv_games

    else:
        # This means we found no games on espn for college football
        # We can just return the directv games at this point since there is nothing from espn
        return directv_games




# Finds the correct channels on comcast for our sports games and adds it to our dictonary
def add_comcast_channels(combined_directv_and_espn_football_games, todays_date):
    for sport in combined_directv_and_espn_football_games:
        for event in combined_directv_and_espn_football_games[sport]:
            channel_number_dictionary = {}
            for network in event.broadcaster:
                if network in comcast_channel_broadcasters:
                    network = comcast_channel_broadcasters[network]
                    if network in comcast_channel_numbers:
                        channel_number_dictionary_entry_form = {'number':'null', 'feed':'null', 'definiton':'standard'}
                        channel_number_dictionary_entry_form['number'] = comcast_channel_numbers[network]
                        channel_number_dictionary_entry_form['definiton'] = "hd"
                        channel_number_dictionary[network] = channel_number_dictionary_entry_form
            event.comcast_channel_number = channel_number_dictionary

    return combined_directv_and_espn_football_games



# Prints out our games to the printer!!!
def print_out(games_to_be_printed_out, todays_date):
    tsv_file_for_gameday_printouts = 'gameday_printouts.tsv'

    # data = ['text1', 'text2', 'text3', 'text4']


    with open(tsv_file_for_gameday_printouts,'w') as write_tsv:
        tsv_writer = csv.writer(write_tsv)

        tsv_writer.writerow(['Sport', 'League', 'Team One', '', 'Team Two', 'Time', 'Directv Channels', 'Comcast Channels'])
        tsv_writer.writerow(['', '', '', '', '', '', '', ''])

        for sport in games_to_be_printed_out:
            tsv_writer.writerow([sport.title(), '', '', '', '', '', '', ''])

            for event in games_to_be_printed_out[sport]:
                tsv_writer.writerow(event.return_for_tsv_printing())


def print_out_xlsx(games_to_be_printed_out, todays_date):
    wb = Workbook()

    # Get the worksheet that is created when we get a workbook
    ws = wb.active

    # Change the title to todays date or something
    ws.title = todays_date

    alignment=Alignment(wrap_text=True,indent=0)

    # add column headings. NB. these must be strings
    ws.append([str(todays_date)])
    ws.append([''])
    ws.append(['Sport', 'League', 'Team One', '', 'Team Two', 'Time', 'Directv Channels', 'Comcast Channels'])

    column_width_dict = {0:0,
                        1:0,
                        2:0,
                        3:0,
                        4:0,
                        5:0,
                        6:0,
                        7:0
                        }

    for sport in games_to_be_printed_out:
        ws.append([sport.title(), '', '', '', '', '', '', ''])

        if len(sport.title()) > column_width_dict[0]:
            column_width_dict[0] = len(sport.title())

        for event in games_to_be_printed_out[sport]:
            ws.append(event.return_for_tsv_printing())

            for column_number, event_data in enumerate(event.return_for_tsv_printing()):
                if len(str(event_data)) > column_width_dict[column_number]:
                    column_width_dict[column_number] = len(str(event_data))


    for row in ws.iter_rows():
        # for cell in row:
        row[6].alignment = alignment
        row[7].alignment = alignment


    for num, col in enumerate(ws.columns):
        if num != 6 or num != 7:
            print num
            ws.column_dimensions[col[0].column_letter].width = column_width_dict[num]

    # openpyxl.worksheet.worksheet.Worksheet.set_printer_settings(ws, paper_size = <someInt>, orientation='por')

    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToHeight = False


    # AFter we are done adding the data to the worksheet, save the workbook
    wb.save('gameday_printouts.xlsx')





def main(zip_code):
    # Maybe in the future derive this timezone based off of zip_code
    local_tz = timezone('Etc/GMT-0')
    today = date.today()
    todays_date = today.strftime("%m-%d-%Y")

    directv_address = Directv_address(todays_date, zip_code)


    directv_games = directv_html_parsing(directv_address.get_address(), todays_date)

    espn_college_football_url = "https://www.espn.com/college-football/schedule/_/year/" + today.strftime("%Y")
    espn_college_football_games = espn_college_football_html_parsing(espn_college_football_url, todays_date, local_tz)

    # Compare the games we found in espn college football games to the football games we found through direct tv. The only outlires should be the games that are showed on the
    # pac12 network because that channel is only on comcast
    # If there are any outliers that arent pac12 network, print them out and analyze why we do have outliers!
    # Add the pac12 network, and other networks not on directv games to the list and if no errors. We should then start printing them out nicely for
    # those to use at the lodge!!!!!!

    combined_directv_and_espn_football_games = compare_add_directv_espn(directv_games, espn_college_football_games)


    # Now find the comcast channels for our sports games!
    games_to_be_printed_out = add_comcast_channels(combined_directv_and_espn_football_games, todays_date)

    # Now take all the sports information and prepare and print it out!
    print_out(games_to_be_printed_out, todays_date)


    print_out_xlsx(games_to_be_printed_out, todays_date)

    #
    # now lets print out what we found!
    #
    print "\n"
    print "This is what we found for sports games for todays date", todays_date + ":"
    print "\n"

    tabbed_print = "    "

    for sport in games_to_be_printed_out:
        print sport
        for event in games_to_be_printed_out[sport]:
            # print tabbed_print, event
            print event.return_for_tsv_printing()

        print "\n"






if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "\n"
        print "ERROR: Too many parameters ran with Game_Day_Print_Out.py"
        print "Correct Usage:   python Game_Day_Print_Out.py [ zip code ]"
        print "\n"
    else:
        main(sys.argv[1])
