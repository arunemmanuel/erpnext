# ERPNext - web based ERP (http://erpnext.com)
# Copyright (C) 2012 Web Notes Technologies Pvt Ltd
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
import webnotes

from utilities.transaction_base import TransactionBase
from home import update_feed

class DocType(TransactionBase):
	def __init__(self, doc, doclist=[]):
		self.doc = doc
		self.doclist = doclist

	def onload(self):
		self.add_communication_list()
	
	def get_sender(self, comm):
		return webnotes.conn.get_value('Email Settings',None,'support_email')
	
	def get_subject(self, comm):
		return '[' + self.doc.name + '] ' + (comm.subject or 'No Subject Specified')
	
	def get_content(self, comm):
		signature = webnotes.conn.get_value('Email Settings',None,'support_signature')
		content = comm.content
		if signature:
			content += '<p>' + signature + '</p>'
		return content
		
	def on_communication_sent(self, comm):
		webnotes.conn.set(self.doc, 'status', 'Waiting for Customer')
		if comm.lead and not self.doc.lead:
			webnotes.conn.set(self.doc, 'lead', comm.lead)
		if comm.contact and not self.doc.contact:
			webnotes.conn.set(self.doc, 'contact', comm.contact)
	
	def close_ticket(self):
		webnotes.conn.set(self.doc,'status','Closed')
		update_feed(self)

	def reopen_ticket(self):
		webnotes.conn.set(self.doc,'status','Open')		
		update_feed(self)
		
	def on_trash(self):
		webnotes.conn.sql("""update `tabCommunication` set support_ticket=NULL 
			where support_ticket=%s""", (self.doc.name,))
