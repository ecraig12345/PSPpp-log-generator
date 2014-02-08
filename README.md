PSP++ log generator
===================

Automates the creation of PSP++ log text files from CSV files. PSP++ 
information, instructions, and source code can be found 
[here](http://www.cs.ou.edu/~rlpage/setools/Tools/PSP++readme.html). 

Running the log generator
-------------------------

If you don't have Python installed, download the appropriate zip file for your 
platform from `executables`, unzip, and double-click the file `psppp_log_gen`. 
(The programs might not work on 32-bit systems.)

If you have Python 2.7 installed (Mac OS X >= 10.8 and recent versions of Linux 
should by default), download `executables/psppp_log_gen.zip` and run from the 
command line with `python psppp_log_gen.zip [args]`. You can view the possible 
arguments using `python psppp_log_gen.zip -h`.

### Team vs. individual mode ###

"Team mode" means that the program will generate a PSP report for an entire 
team. If the "name" column is present in the input time and defect CSV files,
team members' names will be prepended to time and defect entry comments. 
"Individual mode" means that only entries associated with the user's name (or 
entries not associated with any name) will be used. This could be useful if your 
team records their PSP data in the same spreadsheets, but you would like to 
produce a file with only your data.

CSV file creation and formatting
--------------------------------

One possible way to generate CSV files is to make a Google Form with all the 
required fields for a given part of the PSP report. Whenever you want to make a 
PSP entry, fill out the form. The responses to the form will be saved in a 
Google Spreadsheet, which can be downloaded as a CSV file. Here's an 
[example Google Form](https://docs.google.com/forms/d/1Ti2ZmGnsTqZjuhJInaP1_ut-ASHBY0OyuOdRCk7GD30/viewform).

Formatting requirements for CSV files:
- The CSV files must have a header row, and the column names (question names in 
Google Forms) generally must correspond to the names used for each field in the 
PSP++ log text file. Capitalization doesn't matter.
- Valid fields are as follows. (Extra fields will be ignored.) There are examples in the `csv_examples` folder.
	- Time log entries
		- Required: date, start, end, phase, comment
		- Optional: name
	- Defect log entries
		- Required: date, type, fix time, comment
		- Optional: name
	- New object entries
		- Required: name, type, estimated lines
		- Optional: comment
		- An "object type" field with a value of "new" is optional but 
		  recommended if the file contains both new and reused objects. 
	- Reused object entries
		- Required: name, type, estimated base
		- Optional: comment, estimated removed, estimated modified, estimated 
		  added
		- An "object type" field with a value of "reused" is optional but 
		  recommended if the file contains both new and reused objects.
- Dates must be formatted as m/d/yyyy (no leading zeroes). This is what Google 
Forms does. If you're using Excel, you'll need to tell it to use "Text" format 
for date cells, or it will 
- Times must be formatted as h:mm, in *24-hour* time with no leading zero on the 
hour.

Unicode notes
-------------

The code attempts to handle Unicode characters nicely, but it might not be 
incredibly successful in all cases. For best results, either don't use Unicode 
characters (including smart/curly quotes), or be sure to save your files in 
UTF-8 encoding (not Latin 1, Mac OS Roman, or Windows Latin 1). Excel might not 
save files in UTF-8, so use an intelligent text editor, such as TextWrangler for 
Mac or Notepad++ for Windows, to change the encoding if the output text file 
looks strange. You should also replace template/template.html from the PSP++ 
distribution with the one found here if you want Unicode characters to display 
correctly in generated HTML reports.
