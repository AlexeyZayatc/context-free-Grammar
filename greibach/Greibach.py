from Chomsky import Chomsky
from Converter import Converter
from Rule import Rule
from util import *


class Greibach(Converter):
    def __init__(self, grammar):
        super().__init__(grammar)
        self.mapping = dict()
        self.reverse_mapping = dict()

    def convert(self):
        chomsky_converter = Chomsky(self.grammar)
        self.grammar = chomsky_converter.convert()
        self.messages = chomsky_converter.messages

        self.map_non_terminal_to_ordered_symbols()
        self.sort_rules()
        self.remove_left_recursion()
        self.make_rhs_first_symbol_terminal()
        return self.grammar

    def map_non_terminal_to_ordered_symbols(self):
        current_number = 0
        for rule in self.grammar.rules:
            rule_symbols = rule.get_all_rule_symbols()
            for symbol in rule_symbols:
                if is_non_terminal(symbol) and symbol not in self.mapping:
                    self.mapping[symbol] = current_number
                    self.reverse_mapping[current_number] = symbol
                    current_number += 1

    def sort_rules(self):
        while True:
            for index, rule in enumerate(self.grammar.rules):
                if is_non_terminal(rule.rhs[0]) and self.mapping[rule.lhs] > self.mapping[rule.rhs[0]]:
                    indices = self.grammar.find_rules_by_lhs(rule.rhs[0])
                    for idx in indices:
                        new_rule_rhs = self.grammar.rules[idx].rhs + rule.rhs[1:]
                        self.grammar.rules.append(Rule(rule.lhs, new_rule_rhs))
                    self.grammar.rules.remove(rule)
                    break
            else:
                break

    def remove_left_recursion(self):
        while True:
            for index, rule in enumerate(self.grammar.rules):
                if is_non_terminal(rule.rhs[0]) and rule.lhs == rule.rhs[0]:
                    new_non_terminal = self.grammar.get_unused_non_terminal()
                    self.grammar.rules.append(Rule(new_non_terminal, rule.rhs[1:]))
                    self.grammar.rules.append(Rule(new_non_terminal, rule.rhs[1:]+new_non_terminal))

                    indices = self.grammar.find_rules_by_lhs(rule.lhs)
                    for idx in indices:
                        if idx != index:
                            self.grammar.rules.append(Rule(rule.lhs, self.grammar.rules[idx].rhs + new_non_terminal))
                    self.grammar.rules.remove(rule)
                    break
            else:
                break

    def make_rhs_first_symbol_terminal(self):
        while True:
            for index, rule in enumerate(self.grammar.rules):
                if is_non_terminal(rule.rhs[0]):
                    indices = self.grammar.find_rules_by_lhs(rule.rhs[0])
                    for idx in indices:
                        self.grammar.rules.append(Rule(rule.lhs, self.grammar.rules[idx].rhs + rule.rhs[1:]))
                    self.grammar.rules.remove(rule)
                    break
            else:
                break
