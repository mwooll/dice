# dice_visualisation

from bokeh.models import (Div, TextInput, TextAreaInput, Select, Button,
                          DataTable, TableColumn, ColumnDataSource, 
                          HTMLTemplateFormatter)
from bokeh.plotting import curdoc
from bokeh.layouts import column, row

from Dice import Dice
from Hand import Hand
from helper_functions import convert_string_to_int


active_hand = Hand(1)

"""callback functions"""
def handle_dice_input(attr, old, new):
    dice = new.split("\n")
    active_hand.empty_hand()
    for index, die in enumerate(dice):
        try:
            numbers = eval(die)
            assert type(numbers) == list
            active_hand.add_die(numbers, index=index)
            dice_set.text = str(active_hand)
        except ValueError:
            dice_set.text = "please check your input"
        except Exception as e:
            dice_set.text = e
    roll_button.disabled = False


def handle_dice_number(attr, old, new):
    converted = convert_string_to_int(new, 1, 10)
    dice_num_div.text = str(converted)
    if type(converted) == int:
        active_hand._rolls_num = converted

def roll_the_dice():
    active_hand.roll_the_dice(active_hand._rolls_num, " - ")
    result = active_hand.frame_results("split")
    update_table(result)

def update_table(result):
    dice_number = active_hand.get_number_of_dice()
    Columns = [TableColumn(field=col, title=col, width=width_3,
                           formatter=HTMLTemplateFormatter(template='<font colour="<%= CPK %>"><%= value %></font>'))
                    for col in result.columns]

    result_table.columns = Columns
    result_table.source.data = ColumnDataSource.from_df(result)
    result_table.height = 25*active_hand._rolls_num*(dice_number + 2) - 1
    result_table.width = width_3*len(Columns)


    # save the results from the tournament and apply:
    # https://discourse.bokeh.org/t/adding-color-coding-to-individual-columns-on-datatable/3768



"""defining base dimensions"""
width_1  = 300
width_2  = 600
width_3  = 100

height_1 =  50
height_2 = 200
height_3 = 600


"""1st column: input"""

"""dice:"""
dice_input   = TextAreaInput(title="choose the dice to roll", 
                             value="[2, 2, 7, 7, 7]\n[1, 6, 6, 6, 6]\n"
                                  +"[5]\n[4, 4, 4, 4, 9]\n[3, 3, 3, 8, 8",
                             rows=5, width=width_1, height=height_2)
dice_input.on_change("value", handle_dice_input)

dice_number  = TextInput(title="choose the number of dice used per player",
                         value="1", width=50, height=height_1)
dice_number.on_change("value", handle_dice_number)
dice_num_div = Div(text="1", margin=(30, 0, 0, 0), width=250, height=20)

"""tournament:"""
style_select = Select(title="choose the tournament style",
                      options=["all-out", "one die one round"],
                      value="all-out", 
                      width=width_1, height=height_1)

roll_button  = Button(label="roll the dice", disabled=True,
                      width=width_1, height=height_1)
roll_button.on_click(roll_the_dice)

"""visuals"""
colourize_select = Select(title="choose the colouring of the table",
                          options=["all black", "paint by row only",
                                   "paint by column only", "colourful"],
                          value="all black",
                          width=width_1, height=height_1)
# colourize_select.on_change("value", apply_colouring)



"""2nd column: output"""
dice_set     = Div(text="put in some dice", width=width_2, height=height_1)


data_columns = [TableColumn(field="x", title="")]
data_source  = ColumnDataSource({"x": []})

result_table = DataTable(source=data_source,
                         columns=data_columns,
                         index_position=None,
                         width=width_2, height=height_3)
# result_table.autosize_mode = "fit_columns"



"""creating the layout and getting started"""
layout = row(column(dice_input,
                    row(dice_number, 
                        dice_num_div),
                    style_select,
                    colourize_select,
                    roll_button),
             column(dice_set, 
                    result_table))

curdoc().add_root(layout)
curdoc()._set_title("Alakazam's Trickery")
