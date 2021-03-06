title: Einstein's riddle
name: einsteins-riddle
date: 2019-07-05 23:17:00
text:
A friend emailed me [Einstein's riddle](http://udel.edu/~os/riddle.html). He said it took him 25 mins to solve. That gave me a bit of motivation to give it a try. I was at my son's swimming lesson when I read the email and quickly realised that I wasn't going to beat his time. But, as I started solving it with Google Sheets on the iPhone, the idea of using database tables and Sql to generate cartesian product, followed by a process of filtering out untrue data got me intrigued.

It took me well over an hour but it worked and it was fun. *Stop* here and go to the riddle page linked above if you want to give it try.

I used a Sqlite database and below Sql to solve it.

<pre>

/* drink */
insert into drink values('tea')
insert into drink values('coffee')
insert into drink values('milk')
insert into drink values('water')
insert into drink values('beer')

/* house_color */
insert into house_color
	values('red')
insert into house_color
	values('green')
insert into house_color
	values('yellow')
insert into house_color
	values('blue')
insert into house_color
	values('white')

/* house_order */
insert into house_order values(1)
insert into house_order values(2)
insert into house_order values(3)
insert into house_order values(4)
insert into house_order values(5)

/* nationality */
insert into nationality 
	values('brit')
insert into nationality 
	values('swede')
insert into nationality 
	values('dane')
insert into nationality 
	values('norwegian')
insert into nationality 
	values('german')

/* pet */
insert into pet values('dog')
insert into pet values('birds')
insert into pet values('horse')
insert into pet values('cat')
insert into pet values('fish')

/* cigar */
insert into smokes
	values('pall mall');
insert into smokes
	values('dunhill');
insert into smokes
	values('prince');
insert into smokes
	values('blend');
insert into smokes
	values('blue master');

/* create cartesian product of combinations */
/* filter out rows that are untrue */
insert into results
select 
	house_order.Id, nationality.country,
	house_color.color, 
	pet.animal, drink.name, 
	smokes.cigar
from 
	house_order, nationality, 
	house_color, pet, drink, smokes
where 
	pet.animal = 'fish'
	and nationality.country != 'swede'
	and smokes.cigar != 'pall mall'

/* Eliminate more untrue combinations */

/* brit lives in the red house */
delete from results
	where country = 'brit' and color != 'red'
delete from results
	where country != 'brit' and color = 'red'

/* norwegian lives in the 1st house */
delete from results
	where country = 'norwegian' and Id != 1
delete from results
	where country != 'norwegian' and Id = 1

/* Then 2nd house is blue */
delete from results
	where color = 'blue' and Id != 2
delete from results
	where color != 'blue' and Id = 2

/* dane drinks tea */
delete from results
	where country = 'dane' and drink != 'tea'
delete from results
	where country != 'dane' and drink = 'tea'

/* german smokes prince */
delete from results
	where country = 'german' and cigar != 'prince'
delete from results
	where country != 'german' and cigar = 'prince'

/* person in green house drinks coffee */
delete from results
	where color = 'green' and drink != 'coffee'
delete from results
	where color != 'green' and drink = 'coffee'

/* smokes dunhill & lives in the yellow house */
delete from results
	where cigar = 'dunhill' and color != 'yellow'
delete from results
	where cigar != 'dunhill' and color = 'yellow'

/* middle house (id: 3) drinks milk */
delete from results
	where id = 3 and drink != 'milk'
delete from results
	where id != 3 and drink = 'milk'

/* drinks beer smokes blue master */
delete from results
	where drink = 'beer' 
	and cigar != 'blue master'
delete from results
	where drink != 'beer'
	and cigar = 'blue master'

/* green house on the left of the white */
/* 2nd house is blue, */
/* so green, white is 3rd, 4th or 4th, 5th */
delete from results
	where color = 'green' and Id not in (3,4)
delete from results
	where color = 'white' and Id not in (4,5)

/* 15 possibilities left for the fish */
SELECT * from results

Id	country		color	animal	drink	cigar
3	brit		red		fish	milk	blend
4	brit		red		fish	water	blend
5	brit		red		fish	water	blend
4	brit		red		fish	beer	blue master
5	brit		red		fish	beer	blue master
4	dane		yellow	fish	tea		dunhill
5	dane		yellow	fish	tea		dunhill
2	dane		blue	fish	tea		blend
4	dane		white	fish	tea		blend
5	dane		white	fish	tea		blend
1	norwegian	yellow	fish	water	dunhill
4	german		green	fish	coffee	prince
2	german		blue	fish	water	prince
4	german		white	fish	water	prince
5	german		white	fish	water	prince
</pre>

With my son's help, I created tables with pen & paper, filled one column with one of the possibilities, then filled the blanks using hints. When one of the hints conflicted with what we had filled in, we stopped, and repeated the process with the next one. It got faster as we went through them and the 12th row in the list turned out to be the one.

The hand written table looked like:

<style>
table, th, td {
  border: 1px solid black;
}
</style>

 <table>
  <tr>
    <th>1</th>
    <th>2</th>
    <th>3</th>
    <th>4</th>
    <th>5</th>
  </tr>
  <tr>
    <td>norwegian</td>
    <td></td>
    <td>brit</td>
    <td></td>
    <td>german</td>
  </tr>
  <tr>
    <td></td>
    <td>water</td>
    <td>milk</td>
    <td>coffee</td>
    <td></td>
  </tr>
  <tr>
    <td>yellow</td>
    <td>blue</td>
    <td>red</td>
    <td>green</td>
    <td>white</td>
  </tr>
  <tr>
    <td></td>
    <td>horse</td>
    <td>fish</td>
    <td>cat</td>
    <td></td>
  </tr>
  <tr>
    <td>dunhill</td>
    <td></td>
    <td>blend</td>
    <td></td>
    <td>prince</td>
  </tr>
</table>