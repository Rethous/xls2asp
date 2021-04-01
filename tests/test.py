import unittest
import sys
import os
import clingo
import pandas as pd
import subprocess


class Context:
    def id(self, x):
        return x

    def seq(self, x, y):
        return [x, y]

# ------------------------ Ultis functions


def call_xls2asp(silent=False):
    command = 'python xls2asp.py --xls tests/tmp/data.xlsx --template ./tests/tmp/template.txt --output ./tests/tmp/output.lp'
    if silent:
        command_status = subprocess.call(
            command.split(), stderr=subprocess.DEVNULL)
    else:
        command_status = subprocess.call(command.split())
    return command_status


def make_excel(data):
    df1 = pd.DataFrame(data)
    df1.to_excel("./tests/tmp/data.xlsx", index=False)


def make_template(template):
    df1 = pd.DataFrame(template)
    df1.to_csv("./tests/tmp/template.txt", header=None,
               index=None, sep=',', mode='w')


def call_clingo(fact):
    ctl = clingo.Control()
    ctl.load("./tests/tmp/output.lp")
    ctl.add("base", [], ":- not "+fact+".")
    ctl.ground([("base", [])], context=Context())
    models = []
    ctl.solve(on_model=lambda m: models.append(m))
    return models


def check_in_facts(fact):
    models = call_clingo(fact)
    assert (len(models) > 0), "Fact {} not in output".format(fact)


# ------------------------ Tests

def test_general_row():
    make_excel([['Dany', 'Hans', 20, 'male'], [
        'Manuel', 'Vardi', 50, 'male']])
    make_template(
        [['Sheet1', 'row', 'string', 'string', 'int', 'constant']])
    assert call_xls2asp() == 0
    check_in_facts('sheet1("Dany","Hans",20,male)')

def test_general_matrix_xy():
    make_excel(
            [[1, 'Hans', 'Dany', 'Mark'],
             [2, 'Vardi', 'Manuel', 'Paul'],
             [3, 'Mario', 'Morice', 'Peter']])
    make_template(
            [['Sheet1', 'matrix_xy', 'auto_detect', 'auto_detect', 'string']])
    assert call_xls2asp() == 0
    check_in_facts('sheet1(1,2,"Vardi")')
"""
def test_general_sparse_matrix_xy():
    make_excel(
            [['123', 'Hans'], ['Manuel', '321']])
    make_template(
        [['Sheet1', 'sparse_matrix_xy', 'string', 'string']])
    assert call_xls2asp() == 0
    check_in_facts()
"""

def test_time_iso():
    make_excel([['00:20:10'], [
        '18:01:13']])
    make_template(
        [['Sheet1', 'row_indexed', 'time']])
    assert call_xls2asp() == 0
    check_in_facts('sheet1(0,(0,20,10))')
    check_in_facts('sheet1(1,(18,1,13))')

    # Invalid syntax
    make_excel([['100:20:10'], [
        '18:01:13']])
    make_template(
        [['Sheet1', 'row_indexed', 'time']])
    assert call_xls2asp(silent=True) != 0

"""
def test_int_as_string():
    make_excel(
            [['123', 'Hans'], ['Manuel', '321']])
    make_template(
        [['Sheet1', 'row', 'string', 'string']])
    assert call_xls2asp() == 0
    check_in_facts('sheet1("123","Hans")')
    check_in_facts('sheet1("Manuel","321")')
"""
def test_auto_detect():
    make_excel(
            [['123', 'Hans','a'], ['Manuel', '321','b']])
    make_template(
        [['Sheet1', 'row', 'auto_detect', 'auto_detect', 'auto_detect']])
    assert call_xls2asp() == 0
    check_in_facts('sheet1(123,"Hans",a)')
    check_in_facts('sheet1("Manuel",321,b)')

