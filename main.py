﻿# coding=utf-8
import moto
import webapp2
import datetime
import re
import math
from logging import info
from google.appengine.ext import ndb
from google.appengine.api import mail

moto.addfilter("filter.filter")


class base(moto.base):
	pass


class work(moto.workhandler):
	def url(s, p):
		if moto.workhandler.url(s, p):
			s.o.redirect = s.i.redirect
			s.o.error = s.i.error
			s.o.user = s.kget(True)
			s.o.url = s.i.url
			if s.i.id:
				s.o.main = base.getbyid(s.i.id)
			if s.o.main and s.o.main.kusr:
				s.o.make = s.o.main.kusr.get()
			if s.o.user and s.o.main:
				s.o.near = s.o.user.kner.count(s.o.main.key)
			s.o.auth = s.o.user and moto.getenviron("ADMIN_ACCOUNT_EMAIL") == s.o.user.mail
			s.o.mine = s.o.user and (
				(s.o.main and s.o.user.key == s.o.main.key) or (s.o.make and s.o.make.key == s.o.user.key))
			return True

	def page(s, sort, anal, kusr, kint, knerbgn, kfarbgn, knerend, kfarend, attr, gram, page):
		respace = re.compile(u"\s+", re.UNICODE)
		f = base.query(base.anal == anal).order(sort)
		if kusr:
			f = f.filter(base.kusr == kusr)
		if kint:
			f = f.filter(base.kint == kint)
		if knerbgn:
			f = f.filter(base.kslf.IN(knerbgn.get().kner or [0]))
		if kfarbgn:
			f = f.filter(base.kslf.IN(kfarbgn.get().kfar or [0]))
		if knerend:
			f = f.filter(base.kner == knerend)
		if kfarend:
			f = f.filter(base.kner == kfarend)
		if attr:
			for k in respace.split(attr):
				f = f.filter(base.attr == k)
		if gram:
			for k in respace.split(gram):
				f = f.filter(*(base.getgramfilter(k)))
		res = {
			"size": 30,
			"count": f.count(),
		}
		res.update({
			"pagemax": max((res["count"] - 1) / res["size"], 0)
		})
		res.update({
			"page": min(max(int(page or 0), 0), res["pagemax"])
		})
		res.update({
			"fetch": f.fetch(res["size"], offset=res["size"] * res["page"]),
			"pagerng": range(max(res["page"] - 5, 0), 1 + min(res["page"] + 5, res["pagemax"]))
		})
		return res

	def work(s, i, o):
		if s.url("/sign"):
			o.template = "sign"
		if s.url("/late") or s.url("/"):
			o.template = "homelate"
			o.page = s.page(-base.bone, "doga", None, None, None, None, None, None, None, None, i.page)
		if s.url("/qual"):
			o.template = "homequal"
			o.page = s.page(-base.qual, "doga", None, None, None, None, None, None, None, None, i.page)
		if s.url("/attr"):
			o.template = "homeattr"
			o.page = base.query(base.anal == "attr").order(+base.bone).fetch()
		if s.url("/find"):
			if i.t:
				if i.t == u"a": o.a = i.q
				if i.t == u"g": o.g = i.q
			else:
				o.a = i.a
				o.g = i.g
			o.q = o.a or o.g
			o.s = i.s or "new"
			sort = {"new": -base.bone, "old": +base.bone, "god": -base.qual, "bad": +base.qual}
			sort = sort[o.s]
			o.template = "find"
			o.page = s.page(sort, "doga", 0, 0, 0, 0, 0, 0, o.a, o.g, i.page)
		if s.url("/help"):
			o.template = "help"
		if s.url("/test"):
			ndb.put_multi(base.query().order(-base.last).fetch(1000))
		if s.url("/user/qual/#id") or s.url("/user/#id"):
			o.template = "userqual"
			o.page = s.page(-base.qual, "doga", o.main.key, 0, 0, 0, 0, 0, 0, 0, i.page)
		if s.url("/user/late/#id"):
			o.template = "userlate"
			o.page = s.page(-base.bone, "doga", o.main.key, 0, 0, 0, 0, 0, 0, 0, i.page)
		if s.url("/user/clip/#id"):
			o.template = "userclip"
			o.page = s.page(-base.bone, "clip", o.main.key, 0, 0, 0, 0, 0, 0, 0, i.page)
		if s.url("/user/kbgn/#id"):  # フォロワー
			o.template = "userkbgn"
			o.page = s.page(-base.bone, "user", 0, 0, 0, 0, o.main.key, 0, 0, 0, i.page)
		if s.url("/user/kend/#id"):  # フォロー
			o.template = "userkend"
			o.page = s.page(-base.bone, "user", 0, 0, o.main.key, 0, 0, 0, 0, 0, i.page)
		if s.url("/user/doga/#id"):
			o.template = "userdoga"
			if o.mine or o.auth:
				o.doga = moto.getuploadurl("/post/doga/file", 1024 ** 3)
		if s.url("/user/prof/#id"):
			o.template = "userprof"
		if s.url("/user/conf/#id"):
			o.template = "userconf"
		if s.url("/item/#id"):
			if o.main.anal == "clip":
				o.template = "clip"
				o.page = s.page(-base.bone, "doga", 0, 0, 0, 0, 0, 0, 0, 0, i.page)
			if o.main.anal == "doga":
				o.template = "doga"
				o.rice = base.query(base.anal == "rice", base.kint == o.main.key).fetch()
				o.contrice = len(o.rice)
				o.contclip = base.query(base.anal == "clip", base.kner == o.main.key).count()
				o.main.view = (o.main.view or 0) + 1
				o.main.putpoint(o.user)
		if s.url("/post/auth/item") and o.auth:
			if i.cmd == "set":
				o.main.populate(name=i.name, mail=i.mail, text=i.text, word=i.word)
				o.main.put()
			if i.cmd == "del":
				o.main.key.delete()
		if s.url("/post/auth/attr") and o.auth:
			ndb.delete_multi(base.query(base.anal == "attr").fetch(keys_only=True))
			for x in i.attr.split():
				if x and x[0] == "#":
					x = ["#", x[1:]]
				else:
					x = ["", x]
				base(anal="attr", kusr=o.user.key, name=x[1], mail=x[0]).put()
		if s.url("/post/user/new"):
			if base.query(base.anal == "user", base.mail == i.mail).get():
				o.redirect += "?error=the mailaddress is used"
			else:
				o.main = base(anal="user", name=i.name, mail=i.mail, word=i.word)
				o.main.put()
				base(anal="clip", kusr=o.main.key, name=u"最初のクリップ").put()
				o.redirect = "/item/{0}".format(o.main.key.id())
				s.kset(o.main.key)
				mail.send_mail(sender=moto.getdefaultsender(), to=o.main.mail, subject=u"【gorogoro動画】会員情報変更",
				               body=u"会員情報を変更しました。\n名前:{0}\nemail:{1}\npassword:{2}\nゆっくりしていってね_(:3」∠)_".format(
					               o.main.name, o.main.mail, o.main.word))
		if s.url("/post/user/follow") and o.user:
			o.user.kner = filter(lambda x: x != o.main.key, o.user.kner) + ([o.main.key] if i.add else [])
			o.user.put()
		if s.url("/post/user/cok"):
			if i.mail:
				o.main = base.query(base.anal == "user", base.mail == i.mail, base.word == i.word).get()
				if o.main:
					s.kset(o.main.key)
					o.redirect = "/user/{0}".format(o.main.key.id())
				else:
					o.redirect += "?error=No account with the email and password"
			else:
				s.kset(None)
		if s.url("/post/user/set") and o.user:
			o.user.populate(name=i.name, text=i.text)
			if i.image:
				o.user.icon = i.image
			o.user.put()
		if s.url("/post/user/sec") and o.user:
			if o.user.word == i.word:
				o.user.populate(mail=i.newmail, word=i.newword)
				o.user.put()
				mail.send_mail(sender=moto.getdefaultsender(), to=o.user.mail, subject=u"【gorogoro動画】会員情報変更",
				               body=u"会員情報を変更しました。\n名前:{0}\nemail:{1}\npassword:{2}\nゆっくりしていってね_(:3」∠)_".format(
					               o.user.name, o.user.mail, o.user.word))
			else:
				o.redirect += "?error=wrond password"
		if s.url("/post/user/del") and o.user:
			if o.user.word == i.word:
				o.user.key.delete()
				s.kset(None)
			else:
				o.redirect += "?error=wrond password"
		if s.url("/post/doga/new") and o.user:
			o.main = base(anal="doga", name=u"無題", mail="o", kusr=o.user.key, icon=i.image, tlen=float(i.playlen),
			              tpos=float(i.playpos))
			o.main.put()
		if s.url("/post/doga/file"):
			if o.user and not o.main:#投稿時
				o.main = base.query(base.anal == "doga", base.kusr == o.user.key).order(-base.bone).get()
			if o.main and s.blob():
				blob = s.blob()
				blob = sorted(blob, key=lambda x: x.size)
				o.main.size = len(blob)
				o.main.putblob(blob)
		if s.url("/post/doga/conv"):
			o.main = base.query(base.anal=="doga", base.size==1).order(base.last).get()
			if o.main:
				o.main.put()
				o.doga = moto.getuploadurl("/post/doga/file", 1024 ** 3)
		if s.url("/post/doga/attr") and o.user:
			o.main.attr = filter(lambda x: x != i.attr, o.main.attr) + ([i.attr] if i.add else [])
			o.main.put()
			attr = base.query(base.anal == "attr", base.name == i.attr).get()
			if attr:
				attr.size = base.query(base.anal == "doga", base.attr == i.attr).count()
				attr.put()
		if s.url("/post/doga/set") and o.mine:
			o.main.populate(name=i.name, text=i.text, icon=i.image, tlen=float(i.playlen), tpos=float(i.playpos))
			o.main.put()
		if s.url("/post/doga/del") and o.mine:
			o.main.key.delete()
		if s.url("/post/clip/new") and o.user:
			if 10 > base.query(base.anal == "clip", base.kusr == o.user.key).count():
				o.main = base(anal="clip", kusr=o.user.key, name=i.name)
				o.main.put()
			else:
				o.redirect += "?error=you can have 10 clips at most"
		if s.url("/post/clip/del") and o.mine:
			o.main.key.delete()
		if s.url("/post/clip/set") and o.mine:
			if i.name or i.text:
				o.main.populate(name=i.name, text=i.text)
				o.main.put()
			if i.item:
				# 動画
				m = base.getbyid(i.item)
				m.put()
				# 付箋
				info(o.main.kner)
				o.main.kner = filter(lambda x: x != m.key, o.main.kner) + ([m.key] if i.add else [])
				info(o.main.kner)
				o.main.put()
		if s.url("/post/rice/new") and o.user:
			if i.text:
				base(anal="rice", kusr=o.user.key, kint=o.main.key, text=i.text, tpos=float(i.time)).put()
				o.main.put()


app = webapp2.WSGIApplication([('/blob/([^/]+)?', moto.blobhandler), ('/.*', work)])
