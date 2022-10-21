class State:
    def __init__(self, label, isFinal, isInitial=False):
        self.label = label
        self.isInitial = isInitial
        self.isFinal = isFinal

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
        for i in self.transitions:
            if i.state1 == state and i.symbol == symbol:
                sTransitions.append(i)
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

    def convertNFA(self):
        newAutomaton = FA([], self.alphabet, [])
        newAutomaton.initial = self.initial
        newAutomaton.states.append(newAutomaton.initial)
        for X in newAutomaton.states:
            for a in self.alphabet:
                mergedStates = []
                thisTransitions = self.getStateTransitionsSymbol(X, a)
                if len(thisTransitions) > 0:
                    YLabel = ""
                    YIsFinal = False
                    for i in thisTransitions:
                        YLabel += i.state2.label
                        mergedStates.append(i.state2)
                        if not YIsFinal and i.state2.isFinal:
                            YIsFinal = True
                    Y = State(YLabel, YIsFinal)
                    newTransition = Transition(X, Y, a)
                    if not self.compareStates(X, Y):
                        newAutomaton.states.append(Y)
                        if Y.isFinal:
                            newAutomaton.finals.append(Y)
                    newAutomaton.transitions.append(newTransition)
                    for i in mergedStates:
                        for j in self.getStateTransitions(i):
                            newTransitionState1 = Y
                            if self.checkIfStateExists(mergedStates, j.state2):
                                newTransitionState2 = Y
                            else:
                                newTransitionState2 = j.state2
                            newTransition2 = Transition(newTransitionState1, newTransitionState2, j.symbol)
                            if not self.checkIfTransitionExists(newAutomaton.transitions, newTransition2):
                                newAutomaton.transitions.append(newTransition2)

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

    DFA2.printFA()

createTestNFA()