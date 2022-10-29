from cProfile import label
import copy
import os
import re
import PySimpleGUI as sg


class State:
    def __init__(self, label, isFinal, isInitial=False, mergedStates=None, id=""):
        self.label = label
        self.isInitial = isInitial
        self.isFinal = isFinal
        self.mergedStates = mergedStates
        self.id = id

    def printState(self):
        print("[LABEL: " + self.label + ", Final? " + str(self.isFinal) + ", Initial? " + str(self.isInitial) + "]")

    def setId(self, newId):
        self.id = newId


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
    def __init__(self, states, alphabet, transitions):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
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
            for s in state.mergedStates:
                for i in self.transitions:
                    if self.compareStates(i.state1, s) and i.symbol == symbol:
                        cloneI = copy.deepcopy(i)  # Clone object
                        cloneI.setState1(state)  # Set new state1
                        if not self.checkIfTransitionExists(sTransitions,
                                                            cloneI):  # prevent double state in transitions
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
                curTransitions = self.getStateTransitionsSymbol(PC, wordList[0])  # pega transições do atual estado com a letra atual
                if len(curTransitions) == 1:  # se só há uma transição válida para a letra atual
                    PC = curTransitions[0].state2  # avança PC para o próximo estado da transição
                    wordList.pop(0)  # remove letra atual da lista
                    valid = PC.isFinal  # o estado atual é o final?
                else:  # erro, não é AFD!
                    print("INVALID")
                    wordList = []  # esvazia a lista de caracteres da palavra (break)
                    valid = False
                    self.printFA() # calma
                    print(curTransitions)
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
        for i in states:
            if self.compareStates(i, S):
                return True
        return False

    def compareTransitions(self, T1, T2):
        if self.compareStates(T1.state1, T2.state1) and self.compareStates(T1.state2,
                                                                           T2.state2) and T1.symbol == T2.symbol:
            return True
        return False

    def checkIfTransitionExists(self, transitions, T):
        for t in transitions:
            if self.compareTransitions(t, T):
                return True
        return False

    @staticmethod
    def getMergedStates(transitions):
        merged = None
        if len(transitions) > 1:
            merged = []
            for t in transitions:
                merged.append(t.state2)

        return merged

    def addMissingStates(self, usedStates):
        def findStateToRemove(list, stateToRemove):
            for listState in list:
                if self.compareStates(listState, stateToRemove):
                    return listState

        missing = self.states
        for state in usedStates:
            if self.checkIfStateExists(self.states, state):
                missing.remove(findStateToRemove(missing, state))

        return missing

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
                            if not self.checkIsStateExistsInList(statesToProcess, i.state2):
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

        newAutomaton.states += self.addMissingStates(newAutomaton.states)
        return newAutomaton

    def matchState(self, s):
        output = None
        for i in self.states:
            if output is None and i.isFinal == s.isFinal and i.label == s.label:
                output = i
        return output

    def toJffFile(self,fileName):
        if os.path.exists(fileName):
            os.remove(fileName)

        file = open(fileName, "a")
        file.write(
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><!--Created by Camilla + Diogo.--><structure>\n")

        file.write("\t<type>fa</type>\n")
        file.write("\t<automaton>\n")

        file.write("\t\t<!--The list of states.-->\n")
        x = 50
        y = 100
        stateCounter = 0
        for s in self.states:
            s.id = stateCounter  # add id in states
            file.write("\t\t<state id=\"" + str(s.id) + "\" name=\"" + s.label + "\">\n")
            file.write("\t\t\t<x>" + str(x) + ".0</x>\n")
            x += 50
            file.write("\t\t\t<y>" + str(y) + ".0</y>\n")
            y += 30
            if s.isInitial:
                file.write("\t\t\t<initial/>\n")
            if s.isFinal:
                file.write("\t\t\t<final/>\n")
            file.write("\t\t</state>\n")
            stateCounter += 1

        file.write("\t\t<!--The list of transitions.-->\n")
        transitionCounter = 1
        for transition in self.transitions:
            thisState1 = self.matchState(transition.state1)
            thisState2 = self.matchState(transition.state2)
            file.write("\t\t<transition>\n")
            file.write("\t\t\t<from>" + str(thisState1.id) + "</from>\n")
            file.write("\t\t\t<to>" + str(thisState2.id) + "</to>\n")
            file.write("\t\t\t<read>" + transition.symbol + "</read>\n")
            file.write("\t\t</transition>\n")
            file.write("\t\t<!--Transition " + str(transitionCounter) + "-->\n")
            transitionCounter += 1

        file.write("\t</automaton>\n")
        file.write("</structure>")


def fromJffFile(fileName):
    states = []
    transitions = []
    alphabet = set([])

    def getStateFromSubarray(subarray):
        id = re.search('id="(.*)" ', subarray[0]).group(1)
        label = re.search('name="(.*)">', subarray[0]).group(1)

        initial = bool(match for match in subarray if "<initial/>" in match)

        final = bool(match for match in subarray if "<final/>" in match)

        state = State(label=str(label), isFinal=final, isInitial=initial, mergedStates=None, id=id)

        states.append(state)

    def getStateById(id):
        for s in states:
            if s.id == id:
                return s

    def getTransitionFromSubarray(subarray):
        initialId: str = re.search('<from>(.*)</from>', subarray[1]).group(1)
        destinationId: str = re.search('<to>(.*)</to>', subarray[2]).group(1)
        symbol = re.search('<read>(.*)</read>', subarray[3]).group(1)

        transition = Transition(state1=getStateById(initialId), state2=getStateById(destinationId), symbol=symbol)
        transitions.append(transition)
        alphabet.add(symbol)

    file = open(fileName, "r")
    lines = file.readlines()

    for i in range(len(lines)):
        line = lines[i]

        if line.find("<state") != -1:
            stateSubarray = lines[i: i+6]
            getStateFromSubarray(stateSubarray)

        if line.find("<transition") != -1:
            transitionSubarray = lines[i: i + 5]
            getTransitionFromSubarray(transitionSubarray)

    automaton = FA(states, alphabet, transitions)
    return automaton


def createTestDFA():
    S1 = State('A', False, True)
    S2 = State('B', True)

    T1 = Transition(S1, S1, 'a')
    T2 = Transition(S1, S2, 'b')
    T3 = Transition(S2, S2, 'b')
    T4 = Transition(S2, S1, 'a')
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
    print("\nCONVERTED: \n")
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

    print("\nCONVERTED: \n")

    DFA2.printFA()


def createTestNFA3():
    S1 = State('Q0', False, True)
    S2 = State('Q1', False)
    S3 = State('Q2', False)
    S4 = State('Q3', True)

    T1 = Transition(S1, S1, 'a')
    T2 = Transition(S1, S1, 'b')

    T3 = Transition(S1, S2, 'a')
    T4 = Transition(S1, S3, 'b')

    T5 = Transition(S2, S4, 'b')
    T6 = Transition(S3, S4, 'a')

    T7 = Transition(S4, S4, 'a')
    T8 = Transition(S4, S4, 'b')

    ALPHABET = ['a', 'b']
    STATES = [S1, S2, S3, S4]
    TRANSITIONS = [T1, T2, T3, T4, T5, T6, T7, T8]

    NFA1 = FA(STATES, ALPHABET, TRANSITIONS)

    NFA1.printFA()

    DFA2 = NFA1.convertNFA()

    print("\nCONVERTED: \n")

    DFA2.printFA()

    DFA2.toJffFile()


def createFromJffFileTest():
    automaton = fromJffFile()
    automaton.printFA()


###


file_types = [("JFF (*.jff)", "*.jff")]

layout = [

        [sg.Text("Load JFLAP Automaton:")],

        [
            sg.Input(size=(25, 1), key="-FILE-"),
            sg.FileBrowse(file_types=file_types,initial_folder=os.getcwd()),
            sg.Button("OK",key="-LOADDFA-")
        ],


        [sg.Button("Convert to DFA",disabled=True,key="-CONVERT-"),
         sg.Text("Saved converted automaton!",visible=False,key="-SAVENOTIF-")],

        [sg.Text("Validate words to the automaton:")],

        [
            sg.Input(size=(25, 1), key="-WORD-",disabled=True),
            sg.Button("Test Word",disabled=True,key="-TEST-"),
            sg.Text("Valid?"),
            sg.Text("YES",visible=False,key="-WORD_T-"),
            sg.Text("NO",visible=False,key="-WORD_F-")
        ],
    ]
    
window = sg.Window("Automaton Simulator", layout) # Abre a janela

workingAutomaton = None

while True: # Enquanto janela aberta, verificar eventos
    event, values = window.read()

    if event == "Exit" or event == sg.WIN_CLOSED: # Se a janela for fechada, encerrar loop
        break
    
    if event == "-LOADDFA-":
        window['-SAVENOTIF-'].update(visible=False)
        fileName = os.path.basename(values['-FILE-']) 
        print(fileName)
        workingAutomaton = fromJffFile(fileName)
        workingAutomaton.printFA()
        window['-CONVERT-'].update(disabled=False)

    if event == "-CONVERT-":
        if workingAutomaton != None:
            newAutomaton = workingAutomaton.convertNFA()
            workingAutomaton = newAutomaton
            workingAutomaton.printFA()
            workingAutomaton.toJffFile("OUTPUT.jff")
            window['-SAVENOTIF-'].update(visible=True)
            window['-WORD-'].update(disabled=False)
            window['-TEST-'].update(disabled=False)
    
    if event == "-TEST-":
        window['-SAVENOTIF-'].update(visible=False)
        if workingAutomaton != None:
            word = values["-WORD-"]
            valid = workingAutomaton.readWord(word)
            if valid:
                window['-WORD_T-'].update(visible=True)
                window['-WORD_F-'].update(visible=False)
            else:
                window['-WORD_T-'].update(visible=False)
                window['-WORD_F-'].update(visible=True)
