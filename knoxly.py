from flask import Flask, request, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
import knoxlydb
import uuid
import zipfile
import io
import pathlib

app = Flask(__name__)
counter = 0
correct_answers = 0
max_test = 7
user_id = uuid.uuid1()

app.debug = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://wrfdztetneolfz:b25a1aebdddb69d02efb9a8acef25aee8726a08fdc056d47ab8d448372c1b7ed@ec2-99-81-238-134.eu-west-1.compute.amazonaws.com:5432/d5ug0vjnlol6o1'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Sensitivity(db.Model):
	__tablename__ = 'sensitivity'
	id = db.Column(db.String(30), primary_key=True)
	sens_count = db.Column(db.Integer)
	non_sens_count = db.Column(db.Integer)

	def __init__(self, id, sens_count, non_sens_count):
		self.id = id
		self.sens_count = sens_count
		self.non_sens_count = non_sens_count


class Contributors(db.Model):
	__tablename__ = 'contributors'
	id = db.Column(db.Integer, primary_key=True)

	def __init__(self, id):
		self.id = id


@app.route("/")
def home():
	global counter, user_id
	counter = 0
	while db.session.query(Contributors).filter(Contributors.id == user_id.int).count() > 0:
		user_id = uuid.uuid1()
	return render_template('index.html', contributors=3+(db.session.query(Contributors.id).count()))


@app.route('/guidelines')
def guidelines():
	global counter
	counter = 0
	return render_template('guidelines.html')


@app.route("/senstest<id>", methods=['GET', 'POST'])
def senstest(id):
	global counter, racism_show, other_show

	if request.method == 'POST':
		id_tweet = request.form['id_tweet']
		sens = request.form['sens-button']
		if sens and db.session.query(Contributors).filter(Contributors.id == user_id.int).count() > 0:
			knoxlydb.update_sensitivity(id_tweet, sens, db, Sensitivity)

	counter += 1
	tweet = knoxlydb.get_from_db("senstest", 0);
	text = ''.join(tweet[1])
	id_tweet = tweet[0]
	racism_show = 'none'
	other_show = 'inline'
	if tweet[2] == 'Racism':
		racism_show = 'inline'
		other_show = 'none'
	return render_template('senstest.html', tweet_text=text, user_id=user_id.int, id_tweet=id_tweet, id=counter, topic=tweet[2], racism_show=racism_show, other_show=other_show)


@app.route("/test<id>", methods=['GET','POST'])
def test(id):
	global counter, racism_show, other_show, correct_answers, user_id

	while counter < max_test:
		if request.method == 'POST':
			id_tweet = request.form['id_tweet']
			topic = request.form['topic']
			sens = request.form['sens-button']
			if sens:
				if sens == 'Sensitive' or sens == 'Racist':
					guess = 1
				elif sens == 'Non-Sensitive' or sens == 'Non-Racist':
					guess = 0
				res = knoxlydb.check_sensitivity(id_tweet, topic, guess)
				correct_answers += res
				print(f'Value of res: {res} Correct answers: {correct_answers} at iteration {counter}')

		tweet = knoxlydb.get_from_db("test", counter);
		counter += 1
		text = ''.join(tweet[1])
		id_tweet = tweet[0]
		racism_show = 'none'
		other_show = 'inline'
		if tweet[2] == 'Racism':
			racism_show = 'inline'
			other_show = 'none'
		return render_template('test.html', tweet_text=text, user_id=user_id.int, id_tweet=id_tweet, id=counter, topic=tweet[2], racism_show=racism_show, other_show=other_show, pass_show='none', fail_show='none')

	if correct_answers >= 5:
		counter = 0
		knoxlydb.add_contributor(user_id.int, db, Contributors)
		return render_template('test.html', tweet_text='', user_id=user_id.int, id=0, id_tweet=0, topic='', racism_show='none', other_show='none', pass_show='inline', fail_show='none')

	else:
		counter = 0
		return render_template('test.html', tweet_text='', user_id=user_id.int, id=0, id_tweet=0, topic='', racism_show='none', other_show='none', pass_show='none', fail_show='inline')


@app.route('/download-zip')
def request_zip():
	base_path = pathlib.Path('./datasets/')
	data = io.BytesIO()
	with zipfile.ZipFile(data, mode='w') as z:
		for f_name in base_path.iterdir():
			z.write(f_name)
	data.seek(0)
	return send_file(
		data,
		mimetype='application/zip',
		as_attachment=True,
		attachment_filename='data.zip'
	)


if __name__ == "__main__":
	app.run()
