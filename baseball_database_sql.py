import csv
import sqlite3


def main():

	all_star_dict = count_players_by_allstar_game()

	pos_threshold = {'Infield': 4, 'Outfield': 3}

	for year, pos_dict in all_star_dict.iteritems():
		for pos_type, team_dict in pos_dict.iteritems():
			for team_name, player_list in team_dict.iteritems():

				if len(player_list) >= pos_threshold[pos_type]:
					print year, team_name, pos_type, player_list

				# if len(player_list) == pos_threshold[pos_type] - 1:
				#	print 'Almost: ', year, team_name, pos_type, player_list


def count_players_by_allstar_game():
	conn = sqlite3.connect(r"baseball_database.db")
	conn.row_factory = sqlite3.Row
	curs = conn.cursor()

	pos_dict = create_position_dict()
	team_dict = create_team_dict(curs)
	result_dict = {}

	all_star_rows = curs.execute("SELECT * FROM allstar_full GROUP BY playerID, yearID, teamID, startingPos")

	for row in all_star_rows:

		is_starter = False

		try:
			pos_number = int(row['startingPos'])
			pos_type = pos_dict[pos_number]
			is_starter = True

		except:
			pass

		if is_starter:
			try:
				team_name = team_dict[int(row['yearID'])][row['teamID']]
			except:
				print row['yearID']
			add_result_to_dict(row, result_dict, pos_type, team_name)

		else:
			pass

	conn.close()

	return result_dict


def create_position_dict():
	position_dict = dict.fromkeys(range(2, 7), 'Infield')

	for i in range(7, 10):
		position_dict[i] = 'Outfield'

	# Intentionally ignoring the DH 'position'
	# position_dict[0] = 'DH'

	return position_dict


def create_team_dict(curs):

	team_dict = {}

	team_rows = curs.execute("SELECT yearID, teamID, name FROM teams GROUP BY yearID, teamID, name")

	for row in team_rows:

		year_int = int(row['yearID'])

		try:
			team_dict[year_int][row['teamID']] = row['name']
		except:
			team_dict[year_int] = {row['teamID']: row['name']}

	# SFG isn't in the team dict for some reason
	team_dict[2015]['SFG'] = 'San Francisco Giants'

	return team_dict


def add_result_to_dict(row, result_dict, position_type, team):

	year = int(row['yearID'])
	league = row['lgID']
	playerID = row['playerID']

	if year in result_dict.keys():

		if position_type in result_dict[year].keys():
			if team in result_dict[year][position_type].keys():
				result_dict[year][position_type][team].append(playerID)

			else:
				result_dict[year][position_type][team] = [playerID]
		else:
			result_dict[year][position_type] = {team: [playerID]}

	else:
		result_dict[year] = { position_type: {team: [playerID]} }



if __name__ == '__main__':
	main()