class Token:
    def __init__(self, token_lexem:str, token_type:str):
        self.lexem = token_lexem
        self.token_type = token_type

    def __str__(self):
        return '({lexem},{lexem_type})'.format(lexem=self.lexem,lexem_type=self.token_type)
    
    def __lt__(self, other):
        return self.lexem<other.lexem

    def __eq__(self, other):
        if type(other)==Token:
            return other.lexem == self.lexem and other.token_type==self.token_type
        return NotImplemented

    def __ne__(self, other):
        if type(other)==Token:
            return not (other.lexem == self.lexem and other.token_type==self.token_type)
        return NotImplemented

    def __hash__(self):
        isum = 0
        for ch in self.lexem:
            isum+=ord(ch)
        for ch in self.token_type:
            isum+=ord(ch)
        return isum

    def copy(self):
        return Token(self.lexem,self.token_type)
        

def to_array_of_tokens(sstr):
    array_of_tokens = []
    for ch in sstr:
        array_of_tokens.append(Token(ch,'char'))
    if len(array_of_tokens)==0:
        array_of_tokens.append(Token('','char'))
    return array_of_tokens

def to_set_of_tokens(sstr):
    set_of_tokens = set()
    for ch in sstr:
        set_of_tokens.add(Token(ch,'char'))
    return set_of_tokens

def to_dict_of_tokens(rules):
    rules_with_tokens = {}
    for rule in rules:
        temp_arr = []
        for i, rhs in enumerate(rules[rule]):
            temp_arr.append(to_array_of_tokens(rhs))
        rules_with_tokens[Token(rule,'char')]= temp_arr.copy()
    return rules_with_tokens


class CFG:
     def __init__(self, non_terminals, terminals, rules: dict, axiom: str):
        if axiom not in non_terminals:
            raise Exception("Axiom is not in the non-terminals.")
        if not set(rules.keys()).issubset(non_terminals):
            raise Exception("Grammar is not content-independent.")
        for rule_left_side in rules:
            for rule_right_side in rules[rule_left_side]:
                for symbol in rule_right_side:
                    if symbol not in terminals and symbol not in non_terminals:
                        raise Exception("At least one symbol from the right side of the " +
                                        "rules is not in symbols of grammar.")
        # ??????????????????????
        self.non_terminals = to_set_of_tokens(non_terminals)

        # ?????????????????? (?????????? ??????????????, ?????? ???????????? ???????????????? ?????????????? ???????????? ???? ???????????? ??????????????)
        self.terminals = to_set_of_tokens(terminals)

        # ??????????????
        self.rules = to_dict_of_tokens(rules)

        # ?????????????? (?????????????????? ???????????? ????????????????????)
        self.axiom = Token(axiom,'char')
     
     def token_constructor(self, non_term, term, rules, axiom):
         temp = CFG({'A'},{},{},'A')
         temp.non_terminals=non_term.copy()
         temp.terminals=term.copy()
         temp.rules=rules.copy()
         temp.axiom = axiom.copy() 
         return temp
     
     def copy(self):
         return self.token_constructor(self.non_terminals, self.terminals, self.rules, self.axiom)

     def __eq__(self, other):
        if self.non_terminals == other.non_terminals and self.terminals == other.terminals \
                and self.axiom == other.axiom:
            if self.rules.keys()==other.rules.keys():
                for rule in self.rules:
                    if sorted(self.rules[rule])!=sorted(other.rules[rule]):
                        return False
                return True
            else:
                return False
        return False

     def print(self):
        """ ?????????????? ???????????? ????????????????????"""
        print("-" * 18)
        print('Non-terminals: ')
        non_terminals = ""

        for non_terminal in self.non_terminals:
            non_terminals += non_terminal.lexem + ' '

        print(non_terminals)
        print('\n')

        print('Terminals: ')
        terminals = ""

        for terminal in self.terminals:
            terminals += terminal.lexem + ' '

        print(terminals)
        print('\n')

        print('Rules of conclusion: ')

        for left_side in self.rules:
            rule = left_side.lexem + ' -> '
            for i in range(len(self.rules[left_side])):
                if i != len(self.rules[left_side]) - 1:
                    for tkn in self.rules[left_side][i]:
                        rule+=tkn.lexem
                    rule += " | "
                else:
                    for tkn in self.rules[left_side][i]:
                        rule+=tkn.lexem
            print(rule)

        print('\n')

        print("Axiom: " + self.axiom.lexem)
        print(18 * "-")

     def is_contain_good_tokens(self,rhs,good_tokens):
        if not rhs:
            return False
        for token in rhs:
            if token not in self.terminals and token not in good_tokens:
                return False
        return True

     def get_good_non_terminals(self):
        """ ???????????????????? ?????? ?????????????? ?????????????????????? """
        good_tokens = set()
        good_tokens_temp = good_tokens.copy()

        while True:

            # ???????? ???? ???????? ????????????????
            for rule in self.rules:
                for i, rule_item in enumerate(self.rules[rule]):

                    # ???????? ???????????? ?????????? ???????????????? ???????????? ?????????????? ?????????????? ?? ??????????????????,
                    # ???? ?????????????????? ???????????????????? ?? ?????????????? ????????????????
                    if self.is_contain_good_tokens(self.rules[rule][i], good_tokens):
                        good_tokens.add(rule)
                        break

            # ?????????????? ???????????????????? ??????????????????:
            # ???????? ???? ???????????? ???? ???? ???????????????? ???????????????? ???????????? ???????????????? ??????????????
            if good_tokens == good_tokens_temp:
                break

            good_tokens_temp = good_tokens.copy()
        return good_tokens_temp
    
     def is_not_empty(self):
        return self.axiom in self.get_good_non_terminals()

     def remove_bad_non_terminals_and_rules(self):
        good_non_terminals = self.get_good_non_terminals()
        if self.axiom in good_non_terminals:
            # ?????????????????? ?????????????? ????????????
            rules_copy = self.rules.copy()
            for rule in self.rules:

                # ???????? ?????????????????????? ?????? ?? ?????????????? ????????????????,
                # ???? ?????????????? ?????? ???? ??????????????
                if rule not in good_non_terminals:
                    rules_copy.pop(rule)

                # ?????????? ?????????????????? ???????????? ???? ??????????????,
                # ?? ???????????? ???????????? ???????????????? ????????????????????
                # ???????????? ?????????????? ?????????????? ?? ??????????????????
                else:
                    rule_buffer = []
                    for i, rule_item in enumerate(self.rules[rule]):
                        if self.is_contain_good_tokens(rule_item, good_non_terminals):
                            rule_buffer.append(rule_item)

                    rules_copy[rule] = rule_buffer
            return self.token_constructor(good_non_terminals, self.terminals, rules_copy, self.axiom)
        else:
            return None
    
     def remove_unreachable_symbols(self):
        """ ???????????????????? ???????????????????? ?????? ???????????????????????? ???????????????? (?????? ???????? ???????????????? ???????????????????? ???? ????????????) """
        # ???????????????????? ??????????????????????
        reachable_non_terminals = {self.axiom}

        # ????????????????????????, ?????????? ???? ???????????????????? ???? ?????????? ?? ?????? ???? ???????????????????????? ???? ???????????? ????????????????
        reachable_non_terminals_original = reachable_non_terminals.copy()

        # ???????????????????? ??????????????????
        reachable_terminals = set()

        while True:
            for rule_left_side in self.rules:

                # ???????????????????? ???? ???????????????? ?? ??????????????????,
                # ???????? ???? ?????????? ?????????????? ?????????????? ?? ???????????????????? ????????????????????????
                if rule_left_side in reachable_non_terminals_original:
                    for rule_output in self.rules[rule_left_side]:

                        # ???????????????????? ???? ?????????????? ?????????????? ?? ?????????????????? ?????????????? ???? ???????? ?????????????? ?? ????????????????????
                        for symbol in rule_output:
                            if symbol in self.terminals:
                                reachable_terminals.add(symbol)
                            if symbol in self.non_terminals:
                                reachable_non_terminals_original.add(symbol)

            # ?????????????? ?????? ???????????????????? ??????????????????????,
            # ?????????????? ?????? ?????????????????? ?????????? ?????????????? ???????? (difference - ???????????????? ????????????????)
            reachable_non_terminals_original = reachable_non_terminals_original.difference(reachable_non_terminals)

            # ??????????????????, ???????? ???? ?????????????? ?????? ???????????????????? ??????????????????????
            if len(reachable_non_terminals_original) == 0:
                break

            # ???????? ??????, ???? ?????????????????? ???????????????????? ??????????????????????,
            # ?????????????? ???????? ???????????????? ???? ?????????????????? ???????????????? (union - ?????????????????????? ????????????????)
            else:
                reachable_non_terminals = reachable_non_terminals.union(reachable_non_terminals_original)

        # ???????? ???????????????????? ?????????????????????? ?????????????????? ?? ????????,
        # ?????? ???????? ???????????????????? ???????????????????? ?? ????????????????????, ???? ???????????????????? ??????????, ???????????????????? ???????? ????????????????????
        if self.non_terminals == reachable_non_terminals and self.terminals == reachable_terminals:
            return self.copy()

        # ?? ?????????????????? ???????????? ?????????????? ?????????? ?????????????? ????????????,
        # ?? ?????????????? ?????????? ?????? ????????????, ?????????? ??????,
        # ?????? ?????????? ?????????????? ???? ???????????????? ???????????????????? ????????????????????????
        else:
            new_rules = dict()
            for non_terminal in reachable_non_terminals:
                if non_terminal in self.rules:
                    new_rules[non_terminal] = self.rules[non_terminal].copy()

            if len(reachable_non_terminals) == 1 and len(reachable_terminals) == 0 and len(new_rules) == 0:
                new_rules[self.axiom] = [[Token('','char')]]
            # ?? ???????????????????? ?????????????????? ??
            # ?????????????????????? ?????????????????????? ?? ??????????????????????????,
            # ?? ???????????? ?????????????????? ????????????
            return self.token_constructor(reachable_non_terminals, reachable_terminals, new_rules, self.axiom)

     def remove_useless_symbols(self):
        """ ?????????? ?????????????? ????????????????, ??????????????, ??????????????, ?????????????? """
        try:
            without_useless = self.remove_bad_non_terminals_and_rules().remove_unreachable_symbols()
        except Exception as e:
            print(e)
            if type(self.axiom) == Token:
                 return self.token_constructor({self.axiom}, set(), {self.axiom: ['']},self.axiom)
            else:
                 return CFG({self.axiom}, set(), {self.axiom: ['']},self.axiom)
        return without_useless

     def remove_left_recursion(self):
        if  not self.is_not_empty():
            if type(self.axiom) == Token:
                 return self.token_constructor({self.axiom}, set(), {self.axiom: [[Token('','char')]]},self.axiom)
            else:
                 return CFG({self.axiom}, set(), {self.axiom: ['']},self.axiom)

        new_grammar = self.copy()  # ?????????? ???????????????????? ?????????? ???? ??????????????
        new_grammar = new_grammar.remove_useless_symbols()
        new_grammar = new_grammar.remove_chain_rules()
        rule_array = tuple(new_grammar.rules)  # ????????????????????) ??????????????????????
        i = 0  # ?????????????? (?????? ?????? ???????????????)
        while True:
            for o, rule_item in enumerate(new_grammar.rules[rule_array[i]]):  # ???????????????? ???????????? ??????????????
                if rule_item[0] == rule_array[i]:  # ???????? ?????????????? ???????????????? ?????????? ????????????????, ????
                    new_non_terminal = Token(rule_array[i].lexem + '\'','char')  # ?????????????? ?????????? ????????????????????
                    new_non_terminal_rules = []
                    new_rules = []
                    for m, temp_rule in enumerate(
                            new_grammar.rules[rule_array[i]]):  # ???????????????? ?????????? ???? ?????????????? ??????????????
                        if temp_rule[0] == rule_array[i]:  # ???????? ???????????????????? ?????????? ????????????????
                            k = 1
                            #while k < len(temp_rule):  # ?????????????? ???????????? k ???????????????????? ???????????? ??????????????????????
                            #    if temp_rule[k] == rule_array[i]:
                            #        k += 1
                            #    else:
                            #        break

                            new_temp_rule = (
                                temp_rule[k:len(temp_rule)])  # ?????????????????? ???????????? ???????????? ??????????, ?????????? k ????????????????????
                            new_non_terminal_rules.append(
                                new_temp_rule)  # ?????????????????? ?????? ?????????????? ?? ?????????????? ???????????? ??????????????????????
                            temp_list = new_temp_rule.copy()
                            temp_list.append(
                                new_non_terminal)  # ?????????????? ???????????? ?????????? ?? ???????????? ?????????????? (?????????? ???????? ?????????? ???????? ???????????????? ?????????????? ???? ?????????????? (???? ???????? ?????????????????? ???? 2 ????????????????))
                            new_non_terminal_rules.append(temp_list)  # ?????????????????? ?????? ?? ?????????????? ???????????? ??????????????????????
                        else:  # ???????? ?????????????? ???? ???????????????? ?????????? ????????????????, ???? ?????????????????? ?????? ?????? ????????
                            new_rules.append(
                                temp_rule)  # (???????????? ?????? ?????? ?????????? ???????????? ??????????, ???? ?? ?????????? ?? ?????????? ???? ????????????????)
                            temp_list = temp_rule.copy()
                            temp_list.append(new_non_terminal)  # ?????????????????? ?????????????? ?? ???????????????????????? ???? ?????????????? ?? ??????????
                            new_rules.append(temp_list)
                    new_grammar.rules[rule_array[i]] = new_rules  # ?????????????????? ?????????????? ?? ???????????????????????? ??????????????????????
                    new_grammar.non_terminals.add(new_non_terminal)
                    new_grammar.rules.update(
                        {new_non_terminal: new_non_terminal_rules})  # ?????????????????? ?????????? ???????????????????? ?? ?????? ??????????????????
                    break
                else:
                    pass
            if i == len(rule_array) - 1:  # ?????????? ???? ??????????????????
                break
            j = 0
            i += 1
            while True:
                temp_rule = {rule_array[i]: []}  # ?????????????????? ??????????????
                for o, rule_item in enumerate(new_grammar.rules[rule_array[i]]):
                    if rule_item[0] == rule_array[j]:  # ???????? ?? ?????????? ?????????????? ?? ???????????? ?????????? ????????????????????,
                        # ?????????????? ?????????? ???????????? ????????????, ???? ???????????????? ?????? ???? ???????????? ?????????? ???????????? ???? ????????
                        for n, rule_item_temp in enumerate(new_grammar.rules[rule_array[j]]):
                            temp_right_side = rule_item_temp.copy()
                            k = 1
                            #while k < len(rule_item):  # ?????????????? ???????????? k ???????????????????? ???????????? ??????????????????????
                            #    # (???? ????????????????, ?????????? ???? ?????? ???????? ?????????????? ???? ??????????)
                            #    if rule_item[k] == rule_array[j]:
                            #        k += 1
                            #    else:
                            #        break
                            for k in range(k,len(rule_item)):
                                temp_right_side.append(rule_item[k])
                            if len(temp_right_side) >0:
                                temp_rule[rule_array[i]].append(temp_right_side)
                    else:  # ???????? ???? ?????????? ????????????????????, ???? ?????????????????? ?????????????? ?????? ???????? ?????? ??????????????????
                        temp_rule[rule_array[i]].append(rule_item)
                new_grammar.rules.update(temp_rule)  # ??????????????????
                if j == i - 1:
                    break  #
                else:
                    j += 1

        return new_grammar

     def remove_chain_rules(self):
        """ ???????????????????? ???????????????????? ?????? ???????????? ???????????? (?????? ???????? ???????????????? ???????????????????? ???? ????????????) """
        chain_non_terminals = dict()  # ?????? ?????????? ???????????????? ?????? ?????????????????? ???? ???????????? ???????????????????????? (??.??. NA, NB, ... ???? ???????????????????????? ???? ?????????? ???? ?????????? ????????????)

        # ?????????? ?????????????????? chain_non_terminals
        for non_terminal in self.non_terminals:
            chain_non_terminals_key = non_terminal  # ?? ?????????? ?????????????????????? ???????????????????? ?????????????????? ???????????? ???????????????????????? (??????)
            chain_non_terminals_value = set()  # ?????????? ?????????? ?????? ???????????? ?????????????????????? ?????????????????? ???? chain_non_terminals_key
            self.fill_chain_non_terminals_value(chain_non_terminals_key, chain_non_terminals_value,
                                                non_terminal)  # ?????????????????? chain_non_terminals_value (??.??. ???????? ?????? ???????????? ?????????????????????? ?????????????????? ???? chain_non_terminals_key)
            chain_non_terminals[
                chain_non_terminals_key] = chain_non_terminals_value  # "????????????????????" chain_non_terminals_key ?? chain_non_terminals_value

        new_rules = dict()
        for first_chain_non_terminal in chain_non_terminals:  # ???????????????????? ???? ????????????
            # ???????????????????????? ???? ???????? ???????????????? ???????????? ????????????????????????
            rule_outputs = list()  # ?????????? ?????????? ???????????? ?????????? ?????????????? ?? ??????????
            # ???????????????????? ?????????????????? ???? first_chain_non_terminal
            if first_chain_non_terminal in self.rules:
                for rule_output in self.rules[first_chain_non_terminal]:  # ?????????????? ???????????????????? ???? ????????????
                    # ???????????? ???????????? ?????????????????? ???? first_chain_non_terminal
                    if not (len(rule_output) == 1 and rule_output[0] in self.non_terminals):
                        rule_outputs.append(
                            rule_output)  # ?? ?????????????????? ?? rule_outputs ???????????? ??????????,
                        # ?????????????? ???? ?????????????? ???? ???????????? ??????????????????????

                for non_terminal in chain_non_terminals[first_chain_non_terminal]:
                    # ?????????? ???????????????????? ???? ???????????? ???????????? ???????????? ?????????????????? ???? ????????
                    # ?????????????????? ???????????? ???????????????????????? ???? ?????????????????? ?? ???????????? ???????????????????????? first_chain_non_terminal
                    if non_terminal in self.rules:
                        for rule_output in self.rules[non_terminal]:
                            if not (len(rule_output) == 1 and rule_output[0] in self.non_terminals):
                                rule_outputs.append(rule_output)  # ?? ???????????? ???????? ??????????

                if rule_outputs:  # ???????? ???? ????????, ???? ?????????????????? ?? ?????????????? ?????????? ????????????????????
                    new_rules[first_chain_non_terminal] = rule_outputs

        new_grammar = self.copy()
        new_grammar.rules = new_rules
        new_grammar = new_grammar.remove_unreachable_symbols()  # ?????????????????? ???????????????????????? ??????????????
        new_grammar.terminals = self.terminals.copy()  # ?? ?????????????????????????? ???????????????????? ???????????????????? ???????????? ?????????????????????? ?? ?????????????? ????????????
        return new_grammar

     def fill_chain_non_terminals_value(self, key, value,
                                       non_terminal):  # ?????? ?????????? ?? ???????? ?????? ?????? ????????????, ?????????????? ????????????????
        if non_terminal in self.rules:
            for rule_output in self.rules[non_terminal]:
                # ???????????????????? ???? ???????????? ???????????? ???????????? ?????????????????? ???? non_terminal
                # ?? ?????????????????? ?????????????? ???? ?????? ???? ???????????? ??????????????????????
                if len(rule_output) == 1 and rule_output[0] in self.non_terminals:
                    if rule_output[0] not in value and rule_output[0] != key:  # ???????????????? ???? ?????????????????????????? ????????????????
                        value.add(rule_output[0])  # ?? ???????? ??????????????, ???? ?????????????????? ???????? ????????????????????
                        # ?? ?????????????????? ???????????? ???????????????????????? (??????)
                        self.fill_chain_non_terminals_value(key, value, rule_output[
                            0])  # ?? ?????????? ???????? ???????????? ?????????????????????? ?????????????????? ???? ???????????????????????? ?? ?????? ??????????????????????

if __name__ == "__main__":
    A = CFG({'E', 'T', 'F'}, 
            {'+', '(', ')', '*', 'a'},
           {'E': ['', 'T'],
            'T': [''],
           'F': ['(E)', 'a']},
                'E')
    E = CFG({'E', 'T', 'F'}, 
            {'+', '(', ')', '*', 'a'},
           {'E': ['E+T', 'T'],
           'T': ['T*F', 'F'], 
           'F': ['(E)', 'a']},
                'E')
    temp = CFG({'A', 'B', 'C'},
              {'a', 'b'}, 
              {'A': ['BC', 'a'], 
               'B': ['CA', 'Ab'],
              'C': ['AB', 'CC', 'a']},
             'A')
    
    M = CFG({'A', 'B', 'C', 'D'}, {'a', 'b', 'c'},
                {
                    'A': [['A'], ['C'], ['A', 'c'], ['B']],
                    'B': [['C'], ['a']],
                    'C': [['b']]
                },
                'A')
    temp.print()
    temp = temp.remove_left_recursion()
    temp.print()
    test_case1 : CFG = CFG(
    {'S','A','B'},
    {'a','b'},
    {'A' : ['a','ab','B'], 'B' : ['A','Abb','bbaa']},
    'S'
    )
    test_case1.print()
    test_case1 = test_case1.remove_chain_rules()
    test_case1.print()
