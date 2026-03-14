import sqlite3
import sys
import os
import re
#from smtplib import SMTP_SSL as SMTP       # this invokes the secure SMTP protocol (port 465, uses SSL)
from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption)
# old version
# from email.MIMEText import MIMEText
from email.mime.text import MIMEText
#
class CMasterServerDb:
    def __init__(self,Logs,Config,db=None):
        self.Logs = Logs
        self.db='pydarts-masterserver/master-server.db'
        self.Config = Config
        # Connect to db
        self.connect()
        # Purge if requested
        if Config.GetValue('Server','clear-db'):
            self.Logs.Log("WARNING","Squeezing any existing games table in {}".format(self.db))
            sql='DROP table games'
            cur = self.cx.cursor()
            cur.execute(sql)
        # Create structure if needed
        sql='CREATE TABLE IF NOT EXISTS games (id INTEGER PRIMARY KEY AUTOINCREMENT, status INT,creation_timestamp DATETIME, gamename TEXT, gametype TEXT, gamecreator TEXT, serverip TEXT, serverport INT, players INT)';
        cur = self.cx.cursor()
        cur.execute(sql)
        self.cx.commit()
        if self.cx:
            self.cx.close()
#
    def connect(self):
        """ create a database connection to the SQLite database
            specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        try:
            self.cx = sqlite3.connect(self.db)
        except Exception as e:
            self.Logs.Log("ERROR","{}".format(e))
        return None
#
    def get_emails(self):
        """
        Query all rows in the tasks table
        :param conn: the Connection object
        :return:
        """
        self.connect()
        if self.cx:
            cur = self.cx.cursor()
            cur.execute("SELECT mail FROM mails")
            rows = cur.fetchall()
            self.cx.close()
            return rows
#
    def insert_game(self,game):
        self.connect()
        if self.cx:
            #print(game)
            if 'GAMETYPE' not in game:game['GAMETYPE']='UNKNOWN'
            if 'GAMECREATOR' not in game:game['GAMECREATOR']='UNKNOWN'
            sql='INSERT INTO games(status,creation_timestamp,gamename,gametype,gamecreator,serverip,serverport,players) VALUES (1,strftime(\'%Y-%m-%d %H-%M-%S\',\'now\'),"{}","{}","{}","{}",{},{})'.format(game['GAMENAME'],game['GAMETYPE'],game['GAMECREATOR'],game['SERVERIP'],game['SERVERPORT'],game['PLAYERS'])
            #print(sql)
            cur = self.cx.cursor()
            cur.execute(sql)
            self.cx.commit()
            self.cx.close()
#
    def remove_game(self,gamename):
        self.connect()
        if self.cx:
            sql="UPDATE games SET status='0' WHERE gamename='{}'".format(gamename)
            cur = self.cx.cursor()
            cur.execute(sql)
            self.cx.commit()
            self.cx.close()
#
    def close_all_games(self):
        self.connect()
        if self.cx:
            sql="UPDATE games SET status='0'"
            cur = self.cx.cursor()
            cur.execute(sql)
            self.cx.commit()
            self.cx.close()
#
    def delete_game(self,gamename):
        self.connect()
        if self.cx:
            sql="DELETE FROM games WHERE gamename='{}' and status='1'".format(gamename)
            cur = self.cx.cursor()
            cur.execute(sql)
            self.cx.commit()
            self.cx.close()
#
    def add_players(self,gamename,nb):
        self.connect()
        if self.cx:
            sql="UPDATE games SET players=players+{} WHERE gamename='{}' AND status='1'".format(nb,gamename)
            cur = self.cx.cursor()
            cur.execute(sql)
            self.cx.commit()
            self.cx.close()
#
    def remove_players(self,gamename,nb):
        self.connect()
        if self.cx:
            sql="UPDATE games SET players=players-{} WHERE gamename='{}' AND status='1'".format(nb,gamename)
            cur = self.cx.cursor()
            cur.execute(sql)
            self.cx.commit()
            self.cx.close()
#
    def get_games(self):
        self.connect()
        if self.cx:
            sql='SELECT * FROM games WHERE status=1 LIMIT 100'
            cur = self.cx.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            games=[]
            for row in rows:
                # IN CASE OF DB CHANGE, CHANGE HERE, OR SWITCH TO ASSOCIATIVE ARRAY
                game={}
                game['STATUS']=row[1]
                game['GAMENAME']=row[3]
                game['GAMETYPE']=row[4]
                game['GAMECREATOR']=row[5]
                game['SERVERIP']=row[6]
                game['SERVERPORT']=row[7]
                game['PLAYERS']=row[8]
                games.append(game)
            #print(games)
            self.cx.close()
            return games
#
# Class responsible for sending email to registred users
#
class CMail():
    def __init__(self,Logs,ConfigServer):
        self.Logs = Logs
        self.SMTPserver = ConfigServer['notifications-smtp-server']
        self.sender =     ConfigServer['notifications-sender']
        self.reply_to = ConfigServer['notifications-reply']
        self.USERNAME = ""
        self.PASSWORD = ""

        # typical values for text_subtype are plain, html, xml
        self.text_subtype = 'plain'

    def notify_created_game(self,emails,gamename,gametype,gamecreator):
        self.content="Hi !\n"
        self.content+="{} just created a pyDarts network game of {}.\n\n".format(gamecreator,gametype)
        self.content+="The game is called : {}\n".format(gamename)
        self.content+=( "Join fast, or guys will play without you !\n\n"
                        "Your PyDarts' devoted admin :)\n"
                        "Poilou"
                        )
        self.subject="[pyDarts] {} launched a {}".format(gamecreator,gametype)

        for email in emails:
            try:
                msg = MIMEText(self.content, self.text_subtype)
                msg['Subject']= self.subject
                msg['From']   = self.sender # some SMTP servers will do this automatically, not all
                msg.add_header('reply-to', self.reply_to)

                conn = SMTP(self.SMTPserver)
                conn.set_debuglevel(False)
                #conn.login(USERNAME, PASSWORD)
                try:
                    conn.sendmail(self.sender, email, msg.as_string())
                    self.Logs.Log("DEBUG","Successfully notified {} that a game is available".format(email))
                except Exception as e:
                    self.Logs.Log("ERROR","Unable to send email to {}, error was: {}".format(email,e))
            except Exception as e:
                self.Logs.Log("ERROR","Error in email process sending to {}, error was {}".format(email,e))
