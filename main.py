#dice_visualisation

from bokeh.models   import Div, TextInput, TextAreaInput, Select, Button
from bokeh.models   import DataTable, TableColumn, ColumnDataSource
from bokeh.plotting import curdoc
from bokeh.layouts  import column, row

# from Dice import Dice
from Hand import Hand
from helper_functions import convert_string_to_int


active_hand = Hand(1)

"""callback functions"""
def handle_dice_input(attr, old, new) -> None:
    dice = new.split("\n")
    active_hand.empty_hand()
    for die in dice:
        try:
            name, numbers = die.split(":")
            numbers = eval(numbers)
            assert type(numbers) == list
            active_hand.add_die(name, numbers)
            dice_set.text = str(active_hand)
        except ValueError:
            pass
        except AssertionError:
            dice_set.text = "please wrap the faces in a list"
            return
        except Exception as e:
            dice_set.text = e
            return
    roll_button.disabled = False


def handle_dice_number(attr, old, new) -> None:
    converted = convert_string_to_int(new, 1, 10)
    dice_num_div.text = str(converted)
    if type(converted) == int:
        active_hand._rolls_num = converted

def roll_the_dice() -> None:
    active_hand.roll_the_dice(active_hand._rolls_num, 4, " - ")
    result = active_hand.frame_results()
    result_div.text = str(result)
    print(result)

    Columns   = [TableColumn(field=col, title=col) for col in result.columns] # bokeh columns
    data_table = DataTable(columns=Columns, source=ColumnDataSource(result)) # bokeh table


"""defining base dimensions"""
width_1  = 300
width_2  = 800

height_1 =  50
height_2 = 200
height_3 = 600


"""1st column: input"""

# """dice:"""
#     h.add_die("b", [2, 2, 7, 7, 7], "blue")
#     h.add_die("m", [1, 6, 6, 6, 6], "magenta")
#     h.add_die("o", [5, 5, 5, 5, 5], "green")
#     h.add_die("r", [4, 4, 4, 4, 9], "red")
#     h.add_die("y", [3, 3, 3, 8, 8], "white")
dice_input   = TextAreaInput(title="choose the dice to roll", 
                             value="blue: [2, 2, 7, 7, 7]\nmagenta: [1, 6, 6, 6, 6]\n"
                                  +"olive:[5]\nred: [4, 4, 4, 4, 9]\nyellow: [3, 3, 3, 8, 8",
                             rows=5, width=width_1, height=height_2)
dice_input.on_change("value", handle_dice_input)

dice_number  = TextInput(title="choose the number of dice used per player",
                         value="1", width=50, height=height_1)
dice_number.on_change("value", handle_dice_number)
dice_num_div = Div(text="1", margin=(30, 0, 0, 0), width=250, height=20)

"""tournament:"""
style_select = Select(title="choose the tournament style",
                      options=["all-out", "one die one round"], value="all-out", 
                      width=width_1, height=height_1)

roll_button  = Button(label="roll the dice", disabled=True,
                      width=width_1, height=height_1)
roll_button.on_click(roll_the_dice)


"""2nd column: output"""
dice_set     = Div(text="put in some dice", width=width_2, height=height_1)

result_table = DataTable()
result_div   = Div(text="roll the dice to see the results",
                   width=width_1, height=height_3)



layout = row(column(dice_input,
                    row(dice_number, 
                        dice_num_div),
                    style_select,
                    roll_button),
             column(dice_set, 
                    result_div,))
                    # result_table))

curdoc().add_root(layout)
curdoc()._set_title("Alakazam's Trickery")
