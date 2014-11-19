# Dialog system

## Initialization 

Inicialization of the module.

	from dialog import Dialog

	if __name__ == "__main__":
    	DLG = Dialog(globals(), debug=True)
    	DLG.load("example.dlg")
    	DLG.interprete()
    	
We need to share global scope of program to dialog system. It's needed to call functions and use variables from the dialog.


## Dialog description format 

`.dlg` files describes dialog model.

### Identation
Identation defines input or output of the dialog system.

	# this is a comment
	# white-symbol lines ignored

	# identation structure
	Question
		Answer
			Question
				Answer
				
	# few questions at the top level
	Question1
		Answer1
	Question2
		Answer2	

	# both of these Questions triggers Answer
	Question1
	Question2
		Answer
		
	# this question calls two Answers
	Question
		Answer1
			...
		Answer2
			...
	
	# Question calls Answer1 and Answer2
	# ... is Answer2 child, Answer1 has no childs
	Question
		Answer1 
		Answer2
			...
	
	# Question calls Answer1 and Answer2
	# ... is child of Answer1 and Answer2
	Question
		Answer1 &
		Answer2
			...
	

	
	# lower idenation levels are possible
	Question
		Answer
			Question
				Answer
					Question
						Answer
	Question
		Answer
			Question
	Question
		Answer

*Answer isn't obligatory at the last level.*		
Take a look at these identation errors:

	# identation error
	Question
		Answer
				Question
	
	# valid structure, but AnswerX is Question1 child
	Question1
		Answer
			Question
				Answer
	#Question2
		AnswerX
			Question
			

### Random answers

Used to add different possible phrases for the same context.

Not available at the **question-level**. Question-level is zero, even identation level.

	# Question calls Answer3 and one of (Answer1, Answer2, Answer3)
	# with the same probability 33.3%
	Question
		% Answer1
		% Answer2
		Answer3
		% Answer4
	
	# here is possibility of collecting posibility groups
	# 50% between (Answer1, Answer3) and 50% between (Answer2, Answer4)
	Question
		%1 Answer1
		%2 Answer2
		%1 Answer3
		%2 Answer4
		Answer5
		
	# if no identifcator available - it is an empty group
	# 50% between (Answer2, Answer3) and 33.3% between (Answer1, Answer4, Answer5)
	Question
		%1 Answer1
		% Answer2
		% Answer3
		%1 Answer4
		%1 Answer5
	
	# custom probability values
	# calls Answer2, 30% Answer1, 20% Answer4 and 25% between (Answer4, Answer5)
	Question
		30% Answer1
		Answer2
		20% Answer3
		% Answer4	
		% Answer5
	

`TODO possibility between groups`

Usage exmaple:
	
	Hi
	Hello
	Good morning!
		10% Hi
		% Hello

### State flow

Dialog has few states simultaneously. At initial state acceptable questions without identation.

This examples show possible dialog states:

	-> Is pizza delievered?
		Not yet # function binding below
			Call to the courier
				I'm goinng to call the courier
	-> What's the wheater today?
		Shiny, but 15 degrees
			Which clothes do you recommend?
				Sweater and jacket
	
	# possible inputs:
	What's the wheater today?
	Is pizza delievered?
	
	# after phrase Is pizza delievered?:
	# and answer: Not yet
	Is pizza delievered?
		Not yet # function binding below
			-> Call to the courier
				I'm goinng to call the courier
	-> What's the wheater today?
		Shiny, but 15 degrees
			Which clothes do you recommend?
				Sweater and jacket

	??? losing state
	
### Inline data

You can use variables and function defined in code before sharing the global scope. Or varaibles updated during the interpretation.

Python code, somewhere at the global scope:

	def btc_rate():
		rate_eur = get_url_request()
		return rate_eur
	
	cpu_temp = 54


Dialog code:

	What's the current bitcoin rate?
		It's `btc_rate` euros for one bitcoin
	
	What is your CPU temperature?
		`cpu_temp` degrees
		unfortunately not below zero
		
### Set data

#### Fixed data

	`variable_name:Python_literal` 

Can be used anywhere, sets if dialog going thru this phrase. Used in question-leve and answer-level.

Python code, somewhere at the global scope:

	def look_report():
		if not friendly:
			return "You look great, as always"
		else:
			return joke("look")

Dialog code:

	You are annoying `friendly:False`
		Sorry
		
	How i looks like?
		`look_report`

#### Flexible data

	`variable_name~Python_literal` 

Can be used anywhere, sets if dialog going thru this phrase. Used in question-leve and answer-level.

Dialog code:

	...
		What is your name?
			My name is `collocutor~Mark`
				Nice to meet you, `collocutor`

### Routines call

	`function_name?` 

Call is only element at the line at answer-level. Values are at question-level. Activity is at answer-level. ANswers are Python literal.

	`function_name`? # it will generate inline call and append ? to the end
	
This calls aren't locking proceess. They creates Queue, which processed at the same time as user input.

Python code, somewhere at the global scope:

	def make_tea():
		go_to_kitchen()
		check_tea()
		check_water()
		do_manipulations()

Dialog code:

	Make me a tea.
		No problems, i'm gooing to kitchen
		`make_tea?`
			'no tea'
				Sorry there is no tea, can i add tea to your shopping list?
			'no water'
				I can't find water.
				
	# after Make me a tea phrase and response
	# robot calls make_tea function in new subprocess
	# at the input stage checks queue

??? end keyword - needed if we would like use probability to end a dialog

## Cases

### Recognition quality contorol

### Acitivity manager

### Command - clarify - accept

### Explain - stop - interrupt

### I can't do something because

## Link-parser usage

Example of parsing similar word.

	My name is `name~John`

	    +-------->WV------->+
    	+------Wd-----+     |
    	|       +Ds**c+--Ss-+-Ost-+
    	|       |     |     |     |
	LEFT-WALL my.p name.n is.v Mark.b

	[(LEFT-WALL)(my.p)(name.n)(is.v)(Mark.b)]
	[[0 3 2 (WV)][0 2 1 (Wd)][2 3 0 (Ss)][1 2 0 (Ds**c)][3 4 0 (Ost)]]
	[0]


    	+-------->WV------->+
    	+------Wd-----+     |
    	|       +Ds**c+--Ss-+--Ost-+
    	|       |     |     |      |
	LEFT-WALL my.p name.n is.v Pavel[!]

	[(LEFT-WALL)(my.p)(name.n)(is.v)(Pavel[!])]
	[[0 3 2 (WV)][0 2 1 (Wd)][2 3 0 (Ss)][1 2 0 (Ds**c)][3 4 0 (Ost)]]
	[0]

	             +-----Osn-----+
    	+---Wi---+-Ox-+ +-Ds**c+
    	|        |    | |      |
	LEFT-WALL make.v me a sandwich.s

	[(LEFT-WALL)(make.v)(me)(a)(sandwich.s)]
	[[0 1 0 (Wi)][1 4 1 (Osn)][1 2 0 (Ox)][3 4 0 (Ds**c)]]
	[0]

	
	    +------------------Xp------------------+
    	|       +-----I----+-----Osn-----+     |
    	+---Qd--+-SIp+     +-Ox-+ +-Ds**c+     |
    	|       |    |     |    | |      |     |
	LEFT-WALL can.v you make.v me a sandwich.s ?

	[(LEFT-WALL)(can.v)(you)(make.v)(me)(a)(sandwich.s)(?)]
	[[0 7 2 (Xp)][0 1 0 (Qd)][1 3 1 (I)][1 2 0 (SIp)][3 6 1 (Osn)][3 4 0 (Ox)][5 6 0 (Ds**c)]]
	[0]





























	
	
		
	
		
	