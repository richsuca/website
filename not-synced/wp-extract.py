import xml.etree.ElementTree as ET
from datetime import datetime
tree = ET.parse(r'U:\Users\richard\website\richardhsu.wordpress.2016-09-02.xml')
root = tree.getroot()
i = 0

for post in root.iter('item'):
	is_attachment = False
	title = ""
	link = ""
	post_date = ""
	post_name = ""
	content = ""
	
	for child in post:
		if child.tag == 'title':
			if child.text:
				#title = child.text.encode('cp850', errors='replace') #for terminal output
				title = child.text
			else:
				title = '(No Title)'
				
		if child.tag == '{http://wordpress.org/export/1.2/}post_date':
			post_date = child.text
			
		if child.tag == '{http://purl.org/rss/1.0/modules/content/}encoded':
			if (child.text):
				#content = child.text.encode('cp850', errors='replace') #for terminal output
				content = child.text
			else:
				content = "(No Content)"

		if child.tag == '{http://wordpress.org/export/1.2/}post_name':
			post_name = child.text
			
		if child.tag == '{http://wordpress.org/export/1.2/}post_type' and child.text == 'attachment':
			is_attachment = True

	if not is_attachment:
		dated = datetime.strptime(post_date, '%Y-%m-%d %H:%M:%S')
		date_short = dated.strftime('%Y-%m-%d')

		with open(r'U:\Users\richard\website\posts-imported-utf\post-' + date_short + "-" + post_name + '.txt', encoding='utf-8', mode='w') as f:
			f.write("title: " + title + "\n")
			f.write("name: " + post_name + "\n")
			f.write("date: " + post_date + "\n")
			f.write("text:\n" + content)
			
		i += 1
				
print ('Items:' + str(i))