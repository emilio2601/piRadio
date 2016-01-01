#!flask/bin/python
import app
import datetime
import time
import subprocess
import shutil

def record(rec):
	title = rec.title.replace(" ", "_") + ".mp3"
	if rec.tunerID == 1:
		if rec.format == "mp3":
			subprocess.call(["ffmpeg", "-f", "alsa", "-i", "pulse", "-c:a", "libmp3lame", "-b:a", "320k", "-y", "-t", str(rec.duration), title])
			shutil.copyfile(title, "client/recordings/{}".format(title))
			rec.done = True
			rec.download_url = "/recordings/{}".format(title)

			app.db.session.commit()


if __name__ == '__main__':
    while True:
        time.sleep(1)
        recordings = app.Recording.query.all()
        pending_recs = [rec for rec in recordings if not rec.done]
        pending_recs = sorted(pending_recs, key=lambda r: r.date_start)

        now = datetime.datetime.now()
        margin_for_deletion = datetime.timedelta(days=1)
        margin_for_recording = datetime.timedelta(seconds=5)
        for rec in pending_recs:
            if rec.date_start + margin_for_deletion < now: #If recording is pending and a day has passed delete it.
                print("Deleting {}".format(rec))
                app.db.session.delete(rec)
                app.db.session.commit()

            if now - margin_for_recording <= rec.date_start <= now + margin_for_recording:
                print("Recording {}".format(rec))
                record(rec)
