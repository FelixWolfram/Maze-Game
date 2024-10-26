from random import randint


class Question:
    def __init__(self, labyrinth):
        self.labyrinth = labyrinth
        self.questions = [
            ["Schreibt man nä(h)mlich mit h? ", "nein"],
            ["Wie viele Sekunden hat eine Stunde? ", "3600"],
            ["Wie heißt ein Männliches Schwein? ", "Eber"],
            ["Wo ist der kleinste Knochen im Körper? ", "Ohr"],
            ["Wer war der erste Präsident der USA? ", "George Washington"],
            ["Wie viele Bundesländer hat Deutschland? ", "16"],
            ["Was ist die Haupstadt von Bulgarien? ", "Sofia"],
            ["Wie viele Planeten hat unser Sonnensystem? ", "8"],
            ["Wie viele Kontinente gibt es? ", "7"],
            ["Wie viele Knochen hat ein erwachsener Mensch? ", "206"],
            ["Welchen Flächeninhalt hat ein Quadrat mit den Seitenlängen 5LE? ", "25"],
            ["Welches dieser Länder grenzt nicht an Ghana: Nigeria, Togo, Burkina Faso, Liberia: ", "Liberia"],
    ]


    def get_question(self):
        question_index = randint(0, len(self.questions) - 1)
        return self.questions[question_index]
    

    def ask_question(self, player_cell):
        self.labyrinth.draw(player_cell)

        question = self.get_question()
        answer = input(f"\n\n{question[0]}")
        if answer.lower() == question[1].lower():
            self.labyrinth.question_cells.remove(player_cell)  # removint the "?" from the board
            self.questions.remove(question)       # removing the question from the list so it does not appear twice
            return True
        else:
            return False