from colorama import Fore, Back, Style
from colorama import init
from lxml import html
import requests
import random
import csv
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

init(autoreset=True)

link_list = ['https://www.virtualbet24.com/en/predictions/',
'https://www.virtualbet24.com/en/predictions/today/',
'https://www.virtualbet24.com/en/predictions/tomorrow/']

html_tips = ['page/virtualbet_predictions.html', 
'page/virtualbet_predictions_today.html', 
'page/virtualbet_predictions_tomorrow.html']

#```````page download````````````````````````````````````````````````
def page_download(link):
	r_file = link
	page_name = r_file.strip('/').split('/en')[1]
	page_name = page_name.strip('/')
	page_name = page_name.replace('/','_')
	req = requests.get(r_file)
	file = open('page/virtualbet_' + page_name + '.html', 'w', encoding='UTF8')
	new_record = req.text
	file.write(str(new_record))
	file.close()
	print(Style.BRIGHT + Fore.CYAN + f'\nPage with forecasts: {r_file} successfully saved !\n')


#````````program menu````````````````````````````````````````````````
def main_menu():
	while True:
		print('\nMENU >>> ')
		print(Style.BRIGHT + Fore.YELLOW + '`' * 70)
		print('''1.parsing all matches for the near future
2.parsing matches for today
3.parsing matches for tomorrow

4.process and save all matches
5.process and save matches for today
6.process and save matches for tomorrow

7.exit from the program''')
		user_com = input('Your choice (1)...(7) >>> ').strip()
		print()
		if user_com == '1':
			page_download(link_list[0])
		elif user_com == '2':
			page_download(link_list[1])
		elif user_com == '3':
			page_download(link_list[2])
		elif user_com == '4':
			html_csv(html_tips[0])
		elif user_com == '5':
			html_csv(html_tips[1])
		elif user_com == '6':
			html_csv(html_tips[2])
		elif user_com == '7':
			break


#````````parsing html file and saving in сsv`````````````````````````
def html_csv(html_file):
	global list_match, recommend
	list_match = []
	recommend = []

	with open(html_file, 'r', encoding='UTF8') as f:
		contents = f.read()
		soup = BeautifulSoup(contents, 'lxml')
		global title
		title = soup.title.text.split(' - ')[-1]
		title = title.split(' | ')[0].lower()
		title = title.split()
		title = '_'.join(title)

# ````list of all matches on the page````````````````````````````````
		list_matches = soup.find_all('li', class_='padb8')
		for match in list_matches:
			global match_detail
			match_detail = {}
			value_bet = []

#`````````getting information about the date of the match````````````
			date_match_full = match.find('span', class_='date')	
			date_match = date_match_full.get_text()[0:11]
			date_match = datetime.strptime(date_match, '%m-%d %H:%M')	
			date_match = date_match.strftime('%d-%m %H:%M')       
			match_detail['date_match'] = date_match

#```````````home and away team names`````````````````````````````````
			team = date_match_full.get_text()[12:]
			team = team.split('-')

			match_detail['home_team'] = team[0].strip()
			match_detail['away_team'] = team[1].strip()

#`````````match rating information```````````````````````````````````
			rating = match.find('div', class_='rating').get_text()[-2]
			match_detail['rating'] = int(rating)

			home_predict = match.find('span', class_='hpred').get_text().split('@')
			home_value = int(home_predict[0].strip().replace('%', ''))
			home_kef = float(home_predict[1].strip())
			value_bet.append(home_value)

			draw_predict = match.find('span', class_='xpred').get_text().split('@')
			draw_value = int(draw_predict[0].strip().replace('%', ''))
			draw_kef = float(draw_predict[1].strip())
			value_bet.append(draw_value)

			away_predict = match.find('span', class_='apred').get_text().split('@')
			away_value = int(away_predict[0].strip().replace('%', ''))
			away_kef = float(away_predict[1].strip())
			value_bet.append(away_value)

			match_detail['chance_home'] = home_value
			match_detail['home_kef'] = home_kef
			match_detail['chance_draw'] = draw_value
			match_detail['draw_kef'] = draw_kef
			match_detail['chance_away'] = away_value
			match_detail['away_kef'] = away_kef

			tips = match.find('span', class_='pick').get_text()
			match_detail['tips'] = tips

#`````````recommendation system``````````````````````````````````````
			i_max = max(value_bet)
			i_index = value_bet.index(i_max)

			if i_index == 0:
				value = round((i_max * home_kef),2)
			elif i_index == 1:
				value = round((i_max * draw_kef),2)
			elif i_index == 2:
				value = round((i_max * away_kef),2)

#```saving all matches to a list`````````````````````````````````````
			list_match.append(match_detail)

			match_detail['probability value'] = value
			if i_max >= 50 and value >= 100:
				recommend.append(match_detail)

	if len(list_match) > 0:
		df = pd.DataFrame.from_dict(list_match) 
		df.to_csv('data/all_tips_' + title + '.csv', index = False)
		print('all matches: information is processed and stored in a file csv')
	else:
		print('all matches: no information to process')

	if len(recommend) > 0:
		df = pd.DataFrame.from_dict(recommend) 
		df.to_csv('data/recommend_tips_' + title + '.csv', index = False)
		print('recommended matches: information is processed and stored in a file csv')
	else:
		print('recommended matches: no information to process')

	print(f'total matches found: {len(list_match)}')
	print(f'our recommendations: {len(recommend)}')

if __name__ == '__main__':
	main_menu()