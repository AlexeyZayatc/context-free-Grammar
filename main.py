from __future__ import annotations
import pprint
from abc import ABC, abstractmethod
from typing import Union


class Grammar:
    def __init__(self, non_terminals: set, terminals: set, rules: dict, axiom: str):
        if axiom not in non_terminals:
            raise Exception("Axiom is not in the non-terminals.")
        if not set(rules.keys()).issubset(non_terminals):
            raise Exception("Grammar is not content-independent.")
        for rule_left_side in rules:
            for rule_right_side in rules[rule_left_side]:
                for symbol in rule_right_side:
                    if symbol not in terminals and symbol not in non_terminals:
                        raise Exception(
                            "At least one symbol from the right side of the rules is not in symbols of grammar.")
        # нетерминалы
        self.non_terminals = non_terminals

        # терминалы (будем считать, что каждый терминал состоит только из одного символа)
        self.terminals = terminals

        # правила
        self.rules = rules

        # аксиома (начальный символ грамматики)
        self.axiom = axiom

    def __eq__(self, other):
        return self.non_terminals == other.non_terminals and self.terminals == other.terminals and self.rules == other.rules and self.axiom == other.axiom

    def remove_unreachable_symbols(self) -> Grammar:
        """ Возвращает грамматику без недостижимых символов (при этом нынешнюю грамматику не меняет) """
        # достижимые нетерминалы
        reachable_non_terminals = {self.axiom}

        # используется, чтобы не проходится по одним и тем же нетерминалам на каждой итерации
        reachable_non_terminals_original = reachable_non_terminals.copy()

        # достижимые терминалы
        reachable_terminals = set()

        while True:
            for rule_left_side in self.rules:

                # проходимся по правилам и проверяем,
                # есть ли левая сторона правила в достижимых нетерминалах
                if rule_left_side in reachable_non_terminals_original:
                    for rule_output in self.rules[rule_left_side]:

                        # проходимся по выводам правила и добавляем символы из этих выводов в достижимые
                        for symbol in rule_output:
                            if symbol in self.terminals:
                                reachable_terminals.add(symbol)
                            if symbol in self.non_terminals:
                                reachable_non_terminals_original.add(symbol)

            # убираем все достижимые нетерминалы,
            # которые уже проходили через верхний цикл (difference - разность множеств)
            reachable_non_terminals_original = reachable_non_terminals_original.difference(reachable_non_terminals)

            # проверяем, были ли найдены все достижимые нетерминалы
            if len(reachable_non_terminals_original) == 0:
                break

            # если нет, то добавляем достижимые нетерминалы,
            # которые были найденны на последней итерации (union - объединение множеств)
            else:
                reachable_non_terminals = reachable_non_terminals.union(reachable_non_terminals_original)

        # если достижимые нетерминалы совпадают с теми,
        # что были изначально определены в грамматике, то возвращаем новую, идентичную этой грамматику
        if self.non_terminals == reachable_non_terminals and self.terminals == reachable_terminals:
            return self.copy()

        # в противном случае создаем новые правила вывода,
        # в которых будут все старые, кроме тех,
        # чья левая сторона не является достижимым нетерминалом
        else:
            new_rules = dict()
            for non_terminal in reachable_non_terminals:
                if non_terminal in self.rules:
                    new_rules[non_terminal] = self.rules[non_terminal].copy()

            # и возвращаем граматику с
            # достижимыми терминалами и нетерминалами,
            # и новыми правилами вывода
            return Grammar(reachable_non_terminals, reachable_terminals, new_rules, self.axiom)

    def is_contain_nn(self, string: str, symbols: set) -> bool:
        if not string: return False
        for symbol in string:
            if symbol not in self.terminals and symbol not in symbols:
                return False
        return True

    def get_good_non_terminals(self) -> set:
        non_terminals: set = set()
        good_non_terminals: set = non_terminals.copy()

        while True:

            # идем по всем правилам
            for rule in self.rules:
                for i, rule_item in enumerate(self.rules[rule]):

                    # если правая часть содержит только хорошие символы и терминалы,
                    # то добавляем нетерминал к хорошим символам
                    if self.is_contain_nn(self.rules[rule][i], non_terminals):
                        non_terminals.add(rule)
                        break

            # условие прерывания алгоритма:
            # если за проход мы не добавили никакого нового хорошего символа
            if non_terminals == good_non_terminals:
                break

            good_non_terminals = non_terminals.copy()
        return good_non_terminals

    def is_not_empty(self) -> bool:
        return self.axiom in self.get_good_non_terminals()

    def remove_bad_non_terminals_and_rules(self):
        good_non_terminals: set = self.get_good_non_terminals()
        if self.axiom in good_non_terminals:
            # временный словарь правил
            rules_copy = self.rules.copy()
            for rule in self.rules:

                # если нетерминала нет в хороших символах,
                # то удаляем его из словаря
                if rule not in good_non_terminals:
                    rules_copy.pop(rule)

                # иначе оставляет только те правила,
                # в правых частях которого содержатся
                # только хорошие символы и терминалы
                else:
                    rule_buffer = []
                    for i, rule_item in enumerate(self.rules[rule]):
                        if self.is_contain_nn(rule_item, good_non_terminals):
                            rule_buffer.append(rule_item)

                    rules_copy[rule] = rule_buffer
            return Grammar(good_non_terminals, self.terminals, rules_copy, self.axiom)
        else:
            return None

    def remove_useless_symbols(self):
        """ Очень сложный алгоритм, спасибо, Алексей, Евгений """
        try:
            without_useless = self.remove_bad_non_terminals_and_rules().remove_unreachable_symbols()
        except Exception as e:
            print(e)
            return None
        return without_useless

    def remove_left_recursion(self):
        new_grammar = self.copy()  # новая грамматика чтобы её вернуть
        rule_array = tuple(self.rules)  # упорядочил) нетерминалы
        i = 0  # счетчик (кто мог ожидать?)
        while True:
            for o, rule_item in enumerate(new_grammar.rules[rule_array[i]]):  # проверяю каждое правило
                if rule_item[0] == rule_array[i]:  # если правило вызывает левую рекурсию, то
                    new_non_terminal = rule_array[i] + '\''  # создаем новый нетерминал
                    new_non_terminal_rules = []
                    new_rules = []
                    for m, temp_rule in enumerate(
                            new_grammar.rules[rule_array[i]]):  # проходим опять по каждому правилу
                        if temp_rule[0] == rule_array[i]:  # если вызывается левая рекурсия
                            k = 0
                            while k < len(temp_rule):  # скипаем первые k повторений нашего нетерминала
                                if temp_rule[k] == rule_array[i]:
                                    k += 1
                                else:
                                    break
                            if k == len(temp_rule):
                                continue
                            new_temp_rule = (
                            temp_rule[k:len(temp_rule)])  # оставляем только правую часть, после k повторений
                            new_non_terminal_rules.append(
                                new_temp_rule)  # добавляем это правило в правила нового нетерминала
                            temp_list = list(new_temp_rule)
                            temp_list.append(
                                new_non_terminal)  # создаем массив строк с нашего правила (чтобы туда можно было добавить правило со штрихом (то есть состоящее из 2 символов))
                            new_non_terminal_rules.append(temp_list)  # добавляем его в правило нового нетерминала
                        else:  # если правило не вызывает левую рекурсию, то добавляем его как есть
                            new_rules.append(
                                temp_rule)  # (раньше тут был опять массив строк, но я убрал и вроде не ломается)
                            temp_list = list(temp_rule).copy()
                            temp_list.append(new_non_terminal)  # добавляем правило с нетерминалом со штрихом в конце
                            new_rules.append(temp_list)
                    new_grammar.rules[rule_array[i]] = new_rules  # обновляем правила у изначального нетерминала
                    new_grammar.non_terminals.add(new_non_terminal)
                    new_grammar.rules.update(
                        {new_non_terminal: new_non_terminal_rules})  # добавляем новый нетерминал с его правилами
                    break
                else:
                    pass
            if i == len(rule_array) - 1:  # выход из алгоритма
                break
            j = 0
            i += 1
            while True:
                temp_rule = {rule_array[i]: []}  # временные правила
                for o, rule_item in enumerate(new_grammar.rules[rule_array[i]]):
                    if rule_item[0] == rule_array[
                        j]:  # если в нашем правиле в начале стоит нетерминал, который имеет индекс меньше, то заменяем его на правые части правил из НЕГО
                        for n, rule_item_temp in enumerate(new_grammar.rules[rule_array[j]]):
                            if type(rule_item_temp) == type('abc'):
                                temp_right_side = rule_item_temp
                            else:
                                temp_right_side = rule_item_temp.copy()
                            k = 0
                            while k < len(
                                    rule_item):  # скипаем первые k повторений нашего нетерминала (не проверил, может ли тут быть пустота по итогу)
                                if rule_item[k] == rule_array[j]:
                                    k += 1
                                else:
                                    break
                            for k in range(k, len(rule_item)):
                                temp_right_side += rule_item[k]
                            temp_rule[rule_array[i]].append(temp_right_side)
                    else:  # если не стоит нетерминал, то добавляем правило как есть без изменений
                        temp_rule[rule_array[i]].append(rule_item)
                new_grammar.rules.update(temp_rule)  # обновляем
                if j == i - 1:
                    break  #
                else:
                    j += 1

        return new_grammar

    # классы эквивалентности для тестов: 
    # зацикленность (из нетерминала выводится этот же нетерминал)
    # зацикленность (A -> aBC | C; C -> A)
    # нетерминал в выводе не один (A -> B | C)
    # правая часть правила вывода это нетерминал, которого нет в левой части ни одного из правил вывода(т.е. например, A -> Ba; B -> C, и из C нету вывода)
    def remove_chain_rules(self):
        """ Возвращает грамматику без цепных правил (при этом нынешнюю грамматику не меняет) """
        chain_non_terminals = dict()  # тут будут хранится все множества из цепных нетерминалов (т.е. NA, NB, ... по обозначениям из видео по этому алгосу)

        # здесь заполняем chain_non_terminals
        for non_terminal in self.non_terminals:
            chain_non_terminals_key = non_terminal  # с этого нетерминала начинается множество цепных нетерминалов (мцн)
            chain_non_terminals_value = set()  # здесь будут все цепные нетерминалы исходящие из chain_non_terminals_key
            self.fill_chain_non_terminals_value(chain_non_terminals_key, chain_non_terminals_value,
                                                non_terminal)  # заполняем chain_non_terminals_value (т.е. ищем все цепные нетерминалы исходящие из chain_non_terminals_key)
            chain_non_terminals[
                chain_non_terminals_key] = chain_non_terminals_value  # "объединяем" chain_non_terminals_key и chain_non_terminals_value

        new_rules = dict()
        for first_chain_non_terminal in chain_non_terminals:  # проходимся по первым нетерминалам из всех множеств цепных нетерминалов
            rule_outputs = list()  # здесь будут правые части правила в новой грамматике исходящие из first_chain_non_terminal
            if first_chain_non_terminal in self.rules:
                for rule_output in self.rules[
                    first_chain_non_terminal]:  # сначала проходимся по правым частям правил исходящих из first_chain_non_terminal
                    if not (len(rule_output) == 1 and rule_output[0] in self.non_terminals):
                        rule_outputs.append(
                            rule_output)  # и добавляем в rule_outputs правые части, которые не состоят из одного нетерминала

                for non_terminal in chain_non_terminals[
                    first_chain_non_terminal]:  # затем проходимся по правым частям правил исходящих из всех остальных цепных нетерминалов из множества с первым нетерминалом first_chain_non_terminal
                    if non_terminal in self.rules:
                        for rule_output in self.rules[non_terminal]:
                            if not (len(rule_output) == 1 and rule_output[0] in self.non_terminals):
                                rule_outputs.append(rule_output)  # и делаем тоже самое

                if rule_outputs:  # если не пуст, то добавляем в правила новой грамматики
                    new_rules[first_chain_non_terminal] = rule_outputs

        new_grammar = self.copy()
        new_grammar.rules = new_rules
        new_grammar = new_grammar.remove_unreachable_symbols()  # устраняем недостижимые символы
        new_grammar.terminals = self.terminals.copy()  # в возваращаемой грамматике изменяются только нетерминалы и правила вывода
        return new_grammar

    def fill_chain_non_terminals_value(self, key: str, value: set,
                                       non_terminal: str) -> set:  # рот шатал в вайл тру это делать, поэтому рекурсия
        if non_terminal in self.rules:
            for rule_output in self.rules[
                non_terminal]:  # проходимся по правым частям правил исходящих из non_terminal и проверяем состоят ли они из одного нетерминала
                if (len(rule_output) == 1 and rule_output[0] in self.non_terminals):
                    if (rule_output[0] not in value and rule_output[0] != key):  # проверка на зацикленность рекурсии
                        value.add(rule_output[
                                      0])  # и если состоят, то добавляем этот нетерминал в множество цепных нетерминалов (мцн)
                        self.fill_chain_non_terminals_value(key, value, rule_output[
                            0])  # и далее ищем цепные нетерминалы исходящие из добавленного в мцн нетерминала

    def copy(self):
        new_grammar = Grammar(self.non_terminals.copy(), self.terminals.copy(), self.rules.copy(), self.axiom)
        return new_grammar

    def print(self):
        """ Функция печати грамматики"""
        print("-" * 18)
        print('Non-terminals: ')
        non_terminals = ""

        for non_terminal in self.non_terminals:
            non_terminals += non_terminal + ' '

        print(non_terminals)
        print('\n')

        print('Terminals: ')
        terminals = ""

        for terminal in self.terminals:
            terminals += terminal + ' '

        print(terminals)
        print('\n')

        print('Rules of conclusion: ')

        for left_side in self.rules:
            rule = left_side + ' -> '
            for i in range(len(self.rules[left_side])):
                if i != len(self.rules[left_side]) - 1:
                    if type(self.rules[left_side][i]) == type('aaa'):
                        rule += self.rules[left_side][i] + " | "
                    else:
                        for temp_str in self.rules[left_side][i]:
                            rule += temp_str
                        rule += " | "
                else:
                    if type(self.rules[left_side][i]) == type('aaa'):
                        rule += self.rules[left_side][i]
                    else:
                        for temp_str in self.rules[left_side][i]:
                            rule += temp_str

            print(rule)

        print('\n')

        print("Axiom: " + self.axiom)
        print(18 * "-")


if __name__ == '__main__':
    # G = Grammar({'E', 'T', 'F'},
    #             {'a', '(', ')', '+', '*'},
    #             {
    #                 'E': ['F'],
    #                 'F': ['(E)', 'Ta']
    #             },
    #             'E')

    # G.print()

    # F = Grammar({'S'}, {'1', '0'}, {'S': ['0', '1', '0S', '1S']}, 'S')
    F = Grammar({'A'}, {'0'}, {'A': ['']}, 'A')
    # E = Grammar({'S', 'A', 'B', 'C', 'D'}, {'1', '0', '2', '3'},
    #             {'A': ['B', 'A'], 'C': ['D', 'D2'], 'D': ['123', '1', '2', '3']}, 'S')

    # H = Grammar({'A', 'B', 'S'}, {'a', 'b'}, {'S': ['aA'], 'A': ['AB'], 'B': ['b']}, 'S')
    temp = Grammar({'A', 'B', 'C'}, {'a', 'b'}, {'A': ['BC', 'a'], 'B': ['CA', 'Ab'], 'C': ['AB', 'CC', 'a']}, 'A')
    temp.print()
    temp = temp.remove_left_recursion()
    temp.print()
    temp.remove_useless_symbols()
    temp.is_not_empty()
    E = Grammar({'E', 'T', 'F'}, {'+', '(', ')', '*', 'a'}, {'E': ['E+T', 'T'], 'T': ['T*F', 'F'], 'F': ['(E)', 'a']},
                'E')
    E = E.remove_left_recursion()
    E.print()
    E = E.remove_useless_symbols()
    E.print()

    M = Grammar({'A', 'B', 'C', 'D'}, {'a', 'b', 'c'},
                {
                    'A': [['A'], ['C'], ['A', 'c'], ['B']],
                    'B': [['C'], ['a']],
                    'C': [['b']]
                },
                'A')
    M.print()
    M = M.remove_chain_rules()
    M.print()

    L = Grammar(
            {'S','A','B','C'},
            {'1','2','3'},
            {
            'S': ['A'],
            'A': ['B'],
            'B': ['C'],
            },
            'S'
        )
    L.print()
    L = L.remove_unreachable_symbols()
    L.print()
