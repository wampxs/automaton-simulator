import copy

class State:
    def __init__(self, label, isFinal, isInitial=False, mergedStates=None):
        self.label = label
        self.isInitial = isInitial
        self.isFinal = isFinal
        self.mergedStates = mergedStates

    def printState(self):
        print("[LABEL: " + self.label + ", Final? " + str(self.isFinal) + ", Initial? " + str(self.isInitial) + "]")


class Transition:
    def __init__(self, state1, state2, symbol):
        self.state1 = state1
        self.state2 = state2
        self.symbol = symbol

    def printTransition(self):
        print(
            "{TRANSITION: " + self.symbol + ", FROM STATE '" + self.state1.label + "' TO STATE '" + self.state2.label + "'}")

    def setState1(self, newState1):
        self.state1 = newState1


class FA:
    def __init__(self, states, alphabet, transitions, isNFA=False):
        self.states = states
        self.alphabet = [""]
        self.alphabet += alphabet
        self.transitions = transitions
        self.isNFA = isNFA
        self.initial = None
        self.finals = []
        for i in self.states:
            if i.isInitial:
                self.initial = i
                break
        for i in self.states:
            if i.isFinal:
                self.finals.append(i)

    def printFA(self):
        print(self.alphabet)
        for i in self.states:
            i.printState()
        for i in self.transitions:
            i.printTransition()

    def getStateTransitions(self, state):
        sTransitions = []
        for i in self.transitions:
            if i.state1 == state:
                sTransitions.append(i)
        return sTransitions

    def getStateTransitionsSymbol(self, state, symbol):
        sTransitions = []

        if state.mergedStates is None:
            for i in self.transitions:
                if i.state1 == state and i.symbol == symbol:
                    sTransitions.append(i)
        else:
            sTransitions = []
            for s in state.mergedStates:
                for i in self.transitions:
                    if i.state1 == s and i.symbol == symbol:
                        cloneI = copy.deepcopy(i)  # Clone object
                        cloneI.setState1(state)  # Set new state1
                        sTransitions.append(cloneI)

        return sTransitions

    def checkWord(self, word):
        wordList = [c for c in word]
        for i in self.alphabet:
            wordList = [c for c in wordList if c != i]
        if len(wordList) > 0:
            valid = False
        else:
            valid = True
        return valid

    def readWord(self, word):
        valid = False
        if self.checkWord(word):  # se a palavra é válida
            PC = self.initial  # PC = program counter, inicia no estado inicial
            valid = PC.isFinal  # o estado atual é o final?
            wordList = [c for c in word]  # transforma palavra em lista
            while len(wordList) > 0:  # enquanto há letras na palavra
                print(PC.label)
                print(wordList)
                curTransitions = self.getStateTransitionsSymbol(PC, wordList[
                    0])  # pega transições do atual estado com a letra atual
                if len(curTransitions) > 0 and len(
                        curTransitions) < 2:  # se só há uma transição válida para a letra atual
                    PC = curTransitions[0].state2  # avança PC para o próximo estado da transição
                    wordList.pop(0)  # remove letra atual da lista
                    valid = PC.isFinal  # o estado atual é o final?
                else:  # erro, não é AFD!
                    print("INVALID")
                    wordList = []  # esvazia a lista de caracteres da palavra (break)
                    valid = False
            print(PC.label)
            print(wordList)  # imprime lista nessa etapa
        return valid

    @staticmethod
    def compareStates(S1, S2):
        return S1.label == S2.label

    @staticmethod
    def checkIsStateExistsInList(list, stateLooked):
        for state in list:
            if state.label == stateLooked.label:
                return True
        return False

    def checkIfStateExists(self, states, S):
        valid = False
        for i in states:
            if not valid and self.compareStates(i, S):
                valid = True
        return valid

    @staticmethod
    def compareTransitions(T1, T2):
        valid = False
        if T1.state1 == T2.state1 and T1.state2 == T2.state2 and T1.symbol == T2.symbol:
            valid = True
        return valid

    def checkIfTransitionExists(self, transitions, T):
        valid = False
        for i in transitions:
            if not valid and self.compareTransitions(i, T):
                valid = True
        return valid

    def checkLambdas(self):
        valid = True
        for i in self.transitions:
            if valid and i.symbol == "":
                valid = False
        return valid

    @staticmethod
    def getMergedStates(transitions):
        merged = None
        if len(transitions) > 1:
            merged = []
            for t in transitions:
                merged.append(t.state2)

        return merged

    def convertNFA(self):
        newAutomaton = FA([], self.alphabet, [])
        newAutomaton.initial = self.initial
        newAutomaton.states.append(newAutomaton.initial)

        statesToProcess = [newAutomaton.initial]

        for X in statesToProcess:
            for symbol in self.alphabet:

                thisTransitions = self.getStateTransitionsSymbol(X, symbol)

                if len(thisTransitions) > 0:  # If state doesnt have transitions, nothing to do :)
                    YLabel = ""
                    YIsFinal = False

                    for i in thisTransitions:
                        YLabel += i.state2.label
                        if len(thisTransitions) > 1:
                            statesToProcess.append(i.state2)
                        if not YIsFinal and i.state2.isFinal:
                            YIsFinal = True

                    Y = State(YLabel, YIsFinal, mergedStates=self.getMergedStates(thisTransitions))
                    newTransition = Transition(X, Y, symbol)

                    # Check if state already exist in new automaton states
                    if not self.checkIsStateExistsInList(newAutomaton.states, Y):
                        newAutomaton.states.append(Y)
                        if Y.isFinal:  # If state is final, add it to automaton finals
                            newAutomaton.finals.append(Y)

                        # Check if state is in line to be processed
                        if not self.checkIsStateExistsInList(statesToProcess, Y):
                            statesToProcess.append(Y)

                    newAutomaton.transitions.append(newTransition)

        return newAutomaton


def createTestDFA():
    S1 = State('A', False, True)
    S2 = State('B', True)
    T1 = Transition(S1, S1, 'a')
    T2 = Transition(S1, S2, 'b')
    T3 = Transition(S2, S2, 'b')
    T4 = Transition(S2, S1, 'a')
    T5 = Transition(S1, S1, 'b')
    # (a*b*a*)*b
    ALPHABET = ['a', 'b']
    STATES = [S1, S2]
    TRANSITIONS = [T1, T2, T3, T4]

    DFA1 = FA(STATES, ALPHABET, TRANSITIONS)
    print(DFA1.readWord("aba"))
    print("\nDONE\n")


def createTestNFA():
    S1 = State('A', False, True)
    S2 = State('B', True)
    S3 = State('C', True)
    T1 = Transition(S1, S1, 'b')
    T2 = Transition(S1, S2, 'a')
    T3 = Transition(S1, S3, 'a')
    T4 = Transition(S2, S2, 'b')
    T5 = Transition(S3, S3, 'a')

    ALPHABET = ['a', 'b']
    STATES = [S1, S2, S3]
    TRANSITIONS = [T1, T2, T3, T4, T5]
    NFA1 = FA(STATES, ALPHABET, TRANSITIONS)

    NFA1.printFA()

    DFA2 = NFA1.convertNFA()
    print("CONVERTED: ")
    DFA2.printFA()


def createTestNFA2():
    S1 = State('A', False, True)
    S2 = State('B', True)
    T1 = Transition(S1, S1, 'a')
    T2 = Transition(S1, S1, 'b')
    T3 = Transition(S1, S2, 'a')

    ALPHABET = ['a', 'b']
    STATES = [S1, S2]
    TRANSITIONS = [T1, T2, T3]
    NFA1 = FA(STATES, ALPHABET, TRANSITIONS)

    NFA1.printFA()

    DFA2 = NFA1.convertNFA()

    print("CONVERTED: ")

    DFA2.printFA()


createTestNFA2()
