import csv
import pandas as pd
import random as rnd
import random
import cleantweet as ct


datasets = ['./datasets/Health.csv', './datasets/Health2.csv', './datasets/Job.csv', './datasets/Politics.csv', 
			'./datasets/Racism.csv', './datasets/Religion.csv', './datasets/Sexual Orientation.csv', './datasets/Travel.csv']
datasets200 = ['./datasets/200/Health.csv', './datasets/200/Job.csv', './datasets/200/Politics.csv', './datasets/200/Racism.csv', 
				'./datasets/200/Religion.csv', './datasets/200/Sexual Orientation.csv', './datasets/200/Travel.csv']
row = []


def pick_random_row(dataset):
	if '2.csv' in dataset:
		topic = dataset.replace('./datasets/','').replace('2.csv', '')
	else:
		topic = dataset.replace('./datasets/','').replace('.csv', '')
		if '200/' in topic:
			topic = topic.replace('200/', '')
	with open(dataset, 'rt', encoding="utf8") as f:
		reader = csv.reader(f)
		chosen_row = random.choice(list(reader))
		return [chosen_row, topic]


def get_from_db(type, index):
	if type == 'test':
		res = pick_random_row(datasets200[index])
	elif type == 'senstest':
		dataset = random.choice(list(datasets))
		res = pick_random_row(dataset)

	tweet = res[0]
	cleaned_row = ct.clean(tweet[1])
	row.clear()
	return [tweet[0], cleaned_row, res[1]]


def update_sensitivity(id_tweet, sens, db, Sensitivity):

	if sens == 'Sensitive' or sens == 'Racist':
		count_sens = 1
		count_non_sens = 0
	elif sens == 'Non-Sensitive' or sens == 'Non-Racist':
		count_sens = 0
		count_non_sens = 1

	if db.session.query(Sensitivity).filter(Sensitivity.id == id_tweet).count() == 0:
		data = Sensitivity(id_tweet, count_sens, count_non_sens)
		db.session.add(data)
		db.session.commit()
	else:
		update = Sensitivity.query.get(id_tweet)
		update.sens_count = Sensitivity.query.get(id_tweet).sens_count + count_sens
		update.non_sens_count = Sensitivity.query.get(id_tweet).non_sens_count + count_non_sens
		db.session.commit()


def check_sensitivity(id_tweet, topic, guess):
	df = pd.read_csv('./datasets/200/' + topic + '.csv')
	index = df[df['ID'] == id_tweet].index.values[0]
	correct_sens = df.at[index, 'sensibile']
	if correct_sens == guess:
		return 1
	else:
		return 0


def add_contributor(user_id, db, Contributors):
	data = Contributors(user_id)
	db.session.add(data)
	db.session.commit()
