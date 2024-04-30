from aiogram.dispatcher.filters.state import StatesGroup, State


class Command(StatesGroup):
	Mailing = State()
	TestMailing = State()
	TestMailingConfirm = State()
	ConfirmMailing = State()
	ProcessMailing = State()
	Coeff2 = State()
	Coeff3 = State()
	Coeff4 = State()
	Text1Vetka = State()
	Text2Vetka = State()
	Text3Vetka = State()
	Text4Vetka = State()
	TextCard = State()
	TextSBP = State()
	Button1 = State()
	Button2 = State()
	Button3 = State()
	Button4 = State()
	Percent = State()
	SendTrack = State()


class Belenka(StatesGroup):
	LinkNameNumber = State()
	NameUser = State()
	Address = State()
	Phone = State()
	ModelName = State()
	ModelColor = State()
	ModelSize = State()
	ModelPrice = State()
	Screen = State()


class Bosoobuv(StatesGroup):
	LinkNameNumber = State()
	NameUser = State()
	Address = State()
	Phone = State()
	ModelName = State()
	ModelColor = State()
	ModelSize = State()
	ModelPrice = State()
	Screen = State()


class LittleShoes(StatesGroup):
	LinkNameNumber = State()
	NameUser = State()
	Address = State()
	Phone = State()
	ModelName = State()
	ModelColor = State()
	ModelSize = State()
	ModelPrice = State()
	Screen = State()


class Fare(StatesGroup):
	LinkNameNumber = State()
	NameUser = State()
	Address = State()
	Phone = State()
	ModelName = State()
	ModelColor = State()
	ModelSize = State()
	ModelPrice = State()
	Screen = State()


class States(StatesGroup):
	FeedbackText = State()
	FeedbackPhoto = State()
	FeedbackPhoto_Change = State()
	TalkingUser = State()
	TalkingAdmin = State()
	TalkingClientID = State()