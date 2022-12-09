from __future__ import annotations

import pprint
from typing import Union


class Grammar:
    def __init__(self, non_terminals: set, terminals: set, rules: dict, axiom: str):
        if axiom not in non_terminals:
            raise Exception("Axiom is not in the non-terminals.")
        if not set(rules.keys()).issubset(non_terminals):
            raise Exception("Grammar is not content-independent.")

        # нетерминалы
        self.non_terminals = non_terminals

        # терминалы (будем считать, что каждый терминал состоит только из одного символа)
        self.terminals = terminals

        # правила
        self.rules = rules

        # аксиома (начальный символ грамматики)
        self.axiom = axiom

    def __eq__(self,other):
        return self.non_terminals == other.non_terminals and self.terminals==other.terminals and self.rules==other.rules and self.axiom==other.axiom

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
                    for rule in self.rules[rule_left_side]:

                        # проходимся по выводам правила и добавляем символы из этих выводов в достижимые
                        rule_output = rule
                        for char in rule_output:
                            if char in self.terminals:
                                reachable_terminals.add(char)
                            if char in self.non_terminals:
                                reachable_non_terminals_original.add(char)

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
        if self.non_terminals == reachable_non_terminals:
            return Grammar(self.non_terminals.copy(), reachable_terminals.copy(), self.rules.copy(), self.axiom)

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

    def print(self) -> None:
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
                    rule += self.rules[left_side][i] + " | "
                else:
                    rule += self.rules[left_side][i]

            print(rule)

        print('\n')

        print("Аксиома: " + self.axiom)
        print(18 * "-")

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

    def is_not_empty(self) ->  bool:
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

    def copy(self):
        new_grammar = Grammar(self.non_terminals.copy(),self.terminals.copy(), self.rules.copy(),self.axiom)
        return new_grammar

    def remove_left_recursion(self):
        new_grammar = self.copy() #новая грамматика чтобы её вернуть
        rule_array = tuple(self.rules) #упорядочил) нетерминалы
        i = 0 #счетчик (кто мог ожидать?)
        while True:
             for o, rule_item in enumerate(new_grammar.rules[rule_array[i]]): #проверяю каждое правило
                 if rule_item[0] == rule_array[i]: #если правило вызывает левую рекурсию, то
                     new_non_terminal = rule_array[i]+'\'' #создаем новый нетерминал
                     new_non_terminal_rules = []
                     new_rules = [] 
                     for m, temp_rule in enumerate(new_grammar.rules[rule_array[i]]): #проходим опять по каждому правилу
                        if temp_rule[0]==rule_array[i]: #если вызывается левая рекурсия
                             k = 0
                             while k<len(temp_rule): #скипаем первые k повторений нашего нетерминала 
                                 if temp_rule[k]==rule_array[i]: 
                                     k+=1
                                 else:
                                     break
                             if k==len(temp_rule):
                                 continue
                             new_temp_rule = (temp_rule[k:len(temp_rule)]) #оставляем только правую часть,после k повторений 
                             new_non_terminal_rules.append(new_temp_rule)#добавляем это правило в правила нового нетерминала
                             temp_list = list(new_temp_rule)
                             temp_list.append(new_non_terminal) #создаем массив строк с нашего правила (чтобы туда можно было добавить правило со штрихом (то есть состоящее из 2 символов))
                             new_non_terminal_rules.append(temp_list)#добавляем его в правило нового нетерминала
                        else:#если правило не вызывает левую рекурсию, то добавляем его как есть 
                             new_rules.append(temp_rule)  #(раньше тут был опять массив строк, но я убрал и вроде не ломается)
                             temp_list = list(temp_rule).copy() 
                             temp_list.append(new_non_terminal) #добавляем правило с нетерминалом со штрихом в конце
                             new_rules.append(temp_list)
                     new_grammar.rules[rule_array[i]]=new_rules #обновляем правила у изначального нетерминала
                     new_grammar.non_terminals.add(new_non_terminal)
                     new_grammar.rules.update({new_non_terminal : new_non_terminal_rules}) #добавляем новый нетерминал с его правилами
                     break
                 else:
                     pass
             if i==len(rule_array)-1: #выход из алгоритма
                 break
             j = 0
             i+=1
             while True:
                 temp_rule = {rule_array[i] : []} #временные правила
                 for o, rule_item in enumerate(new_grammar.rules[rule_array[i]]):
                     if rule_item[0]==rule_array[j]: #если в нашем правиле в начале стоит нетерминал, который имеет индекс меньше, то заменяем его на правые части правил из НЕГО
                         for n, rule_item_temp in enumerate(new_grammar.rules[rule_array[j]]):
                             if type(rule_item_temp) == type('abc'):
                                 temp_right_side = rule_item_temp
                             else:
                                 temp_right_side = rule_item_temp.copy()
                             k = 0
                             while k<len(rule_item): #скипаем первые k повторений нашего нетерминала (не проверил может ли тут быть пустота по итогу)
                                 if rule_item[k]==rule_array[j]: 
                                     k+=1
                                 else:
                                     break
                             for k in range(k, len(rule_item)):
                                 temp_right_side+=rule_item[k]
                             temp_rule[rule_array[i]].append(temp_right_side)
                     else: #если не стоит нетерминал то добавляем правило как есть без изменений
                         temp_rule[rule_array[i]].append(rule_item)
                 new_grammar.rules.update(temp_rule) #обновляем
                 if j==i-1:
                     break #
                 else:
                     j+=1
             
              
        return new_grammar
       

 


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
    F = Grammar({'A',}, {'0',}, {'A': ['']}, 'A')
    # E = Grammar({'S', 'A', 'B', 'C', 'D'}, {'1', '0', '2', '3'},
    #             {'A': ['B', 'A'], 'C': ['D', 'D2'], 'D': ['123', '1', '2', '3']}, 'S')

    H = Grammar({'A', 'B', 'S'}, {'a', 'b'}, {'S': ['aA'], 'A': ['AB'], 'B': ['b']}, 'S')
    temp = Grammar({'A','B','C'},{'a','b'}, { 'A': ['BC','a'], 'B': ['CA','Ab'], 'C': ['AB', 'CC', 'a']}, 'A')
    temp.print()
    temp = temp.remove_left_recursion()
    pprint.pprint(vars(temp))
    temp.remove_useless_symbols()
    temp.is_not_empty()
    E = Grammar({'E','T','F'},{'+','(',')','*', 'a'},{'E': ['E+T', 'T'], 'T': ['T*F','F'], 'F': ['(E)','a']},'E')
    E = E.remove_left_recursion()
    pprint.pprint(vars(E))
    E = E.remove_useless_symbols()
    pprint.pprint(vars(E))

