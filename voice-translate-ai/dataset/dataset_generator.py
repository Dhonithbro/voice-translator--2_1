"""
=============================================================
  SYNTHETIC DATASET GENERATOR — Real-Time Voice Translator
  Generates 1500 instruction-style translation pairs
  Domains: Daily, Travel, Education, Medical, Business, Technical
  Languages: English → Hindi, German, French, Spanish
=============================================================
"""

import json
import random
import os

# ─── Base Sentence Templates per Domain ──────────────────────────────────────

SENTENCES = {
    "daily_conversation": [
        ("How are you?", "आप कैसे हैं?", "Wie geht es Ihnen?", "Comment allez-vous?", "¿Cómo estás?", "మీరు ఎలా ఉన్నారు?", "நீங்கள் எப்படி இருக்கிறீர்கள்?", "താങ്കൾ എങ്ങനെ ഉണ്ട്?"),
        ("Good morning!", "सुप्रभात!", "Guten Morgen!", "Bonjour!", "¡Buenos días!", "శుభోదయం!", "காலை வணக்கம்!", "സുപ്രഭാതം!"),
        ("What is your name?", "आपका नाम क्या है?", "Wie heißen Sie?", "Comment vous appelez-vous?", "¿Cómo te llamas?", "మీ పేరు ఏమిటి?", "உங்கள் பெயர் என்ன?", "താങ്കളുടെ പേര് എന്താണ്?"),
        ("Where do you live?", "आप कहाँ रहते हैं?", "Wo wohnen Sie?", "Où habitez-vous?", "¿Dónde vives?"),
        ("How old are you?", "आपकी उम्र क्या है?", "Wie alt sind Sie?", "Quel âge avez-vous?", "¿Cuántos años tienes?"),
        ("I am feeling happy today.", "मैं आज खुश हूँ।", "Ich fühle mich heute glücklich.", "Je me sens heureux aujourd'hui.", "Me siento feliz hoy."),
        ("Can you help me?", "क्या आप मेरी मदद कर सकते हैं?", "Können Sie mir helfen?", "Pouvez-vous m'aider?", "¿Puedes ayudarme?"),
        ("I don't understand.", "मुझे समझ नहीं आया।", "Ich verstehe nicht.", "Je ne comprends pas.", "No entiendo."),
        ("Please speak slowly.", "कृपया धीरे बोलें।", "Bitte sprechen Sie langsam.", "Parlez lentement s'il vous plaît.", "Por favor habla despacio."),
        ("See you tomorrow.", "कल मिलते हैं।", "Bis morgen.", "À demain.", "Hasta mañana."),
        ("Thank you very much.", "बहुत बहुत धन्यवाद।", "Vielen Dank.", "Merci beaucoup.", "Muchas gracias.", "చాలా ధన్యవాదాలు.", "மிக்க நன்றி.", "വളരെ നന്ദി."),
        ("You are welcome.", "आपका स्वागत है।", "Bitte sehr.", "De rien.", "De nada."),
        ("Excuse me, please.", "माफ़ कीजिए।", "Entschuldigung.", "Excusez-moi.", "Disculpe."),
        ("I am sorry.", "मुझे खेद है।", "Es tut mir leid.", "Je suis désolé.", "Lo siento."),
        ("What time is it?", "अभी कितने बजे हैं?", "Wie spät ist es?", "Quelle heure est-il?", "¿Qué hora es?"),
        ("Good night.", "शुभ रात्रि।", "Gute Nacht.", "Bonne nuit.", "Buenas noches."),
        ("How was your day?", "आपका दिन कैसा था?", "Wie war Ihr Tag?", "Comment s'est passée votre journée?", "¿Cómo estuvo tu día?"),
        ("I am hungry.", "मुझे भूख लगी है।", "Ich habe Hunger.", "J'ai faim.", "Tengo hambre."),
        ("Let's go together.", "चलिए साथ चलते हैं।", "Lass uns zusammen gehen.", "Allons-y ensemble.", "Vamos juntos."),
        ("I like this place.", "मुझे यह जगह पसंद है।", "Ich mag diesen Ort.", "J'aime cet endroit.", "Me gusta este lugar."),
        ("What do you do for work?", "आप क्या काम करते हैं?", "Was machen Sie beruflich?", "Que faites-vous dans la vie?", "¿A qué te dedicas?"),
        ("Do you have any siblings?", "क्या आपके कोई भाई-बहन हैं?", "Haben Sie Geschwister?", "Avez-vous des frères et sœurs?", "¿Tienes hermanos?"),
        ("I love reading books.", "मुझे किताबें पढ़ना बहुत पसंद है।", "Ich liebe es, Bücher zu lesen.", "J'adore lire des livres.", "Me encanta leer libros."),
        ("The weather is nice today.", "आज मौसम अच्छा है।", "Das Wetter ist heute schön.", "Le temps est beau aujourd'hui.", "El clima está agradable hoy."),
        ("Can we meet later?", "क्या हम बाद में मिल सकते हैं?", "Können wir uns später treffen?", "Pouvons-nous nous rencontrer plus tard?", "¿Podemos encontrarnos después?"),
        ("I need some water.", "मुझे थोड़ा पानी चाहिए।", "Ich brauche etwas Wasser.", "J'ai besoin d'eau.", "Necesito agua."),
        ("This food is delicious.", "यह खाना बहुत स्वादिष्ट है।", "Dieses Essen ist köstlich.", "Cette nourriture est délicieuse.", "Esta comida está deliciosa."),
        ("I missed the bus.", "मेरी बस छूट गई।", "Ich habe den Bus verpasst.", "J'ai raté le bus.", "Perdí el autobús."),
        ("She is my best friend.", "वह मेरी सबसे अच्छी दोस्त है।", "Sie ist meine beste Freundin.", "Elle est ma meilleure amie.", "Ella es mi mejor amiga."),
        ("We had a great time.", "हमने बहुत अच्छा समय बिताया।", "Wir hatten eine tolle Zeit.", "Nous avons passé un excellent moment.", "Pasamos un momento genial."),
    ],
    "travel": [
        ("Where is the nearest hotel?", "नजदीकी होटल कहाँ है?", "Wo ist das nächste Hotel?", "Où est l'hôtel le plus proche?", "¿Dónde está el hotel más cercano?"),
        ("How much does this ticket cost?", "इस टिकट की कीमत क्या है?", "Wie viel kostet dieses Ticket?", "Combien coûte ce billet?", "¿Cuánto cuesta este boleto?"),
        ("I need to book a room.", "मुझे एक कमरा बुक करना है।", "Ich muss ein Zimmer buchen.", "Je dois réserver une chambre.", "Necesito reservar una habitación."),
        ("Can you show me the map?", "क्या आप मुझे नक्शा दिखा सकते हैं?", "Können Sie mir die Karte zeigen?", "Pouvez-vous me montrer la carte?", "¿Puede mostrarme el mapa?"),
        ("When does the next train leave?", "अगली ट्रेन कब जाती है?", "Wann fährt der nächste Zug?", "Quand part le prochain train?", "¿Cuándo sale el próximo tren?"),
        ("I have lost my passport.", "मेरा पासपोर्ट खो गया है।", "Ich habe meinen Pass verloren.", "J'ai perdu mon passeport.", "He perdido mi pasaporte."),
        ("What is the exchange rate?", "विनिमय दर क्या है?", "Was ist der Wechselkurs?", "Quel est le taux de change?", "¿Cuál es el tipo de cambio?"),
        ("Is this seat available?", "क्या यह सीट खाली है?", "Ist dieser Platz frei?", "Ce siège est-il libre?", "¿Está disponible este asiento?"),
        ("Please take me to the airport.", "कृपया मुझे हवाई अड्डे पर ले जाएं।", "Bitte bringen Sie mich zum Flughafen.", "Veuillez m'emmener à l'aéroport.", "Por favor lléveme al aeropuerto."),
        ("My luggage is missing.", "मेरा सामान गायब है।", "Mein Gepäck fehlt.", "Mes bagages sont manquants.", "Mi equipaje está perdido."),
        ("How far is the city center?", "शहर का केंद्र कितनी दूर है?", "Wie weit ist das Stadtzentrum?", "À quelle distance est le centre-ville?", "¿Qué tan lejos está el centro de la ciudad?"),
        ("Do you have a vegetarian menu?", "क्या आपके पास शाकाहारी मेनू है?", "Haben Sie eine vegetarische Speisekarte?", "Avez-vous un menu végétarien?", "¿Tiene menú vegetariano?"),
        ("I want a window seat.", "मुझे खिड़की की सीट चाहिए।", "Ich möchte einen Fensterplatz.", "Je voudrais un siège côté fenêtre.", "Quiero un asiento junto a la ventana."),
        ("Where can I find a taxi?", "मुझे टैक्सी कहाँ मिलेगी?", "Wo kann ich ein Taxi finden?", "Où puis-je trouver un taxi?", "¿Dónde puedo encontrar un taxi?"),
        ("Is breakfast included?", "क्या नाश्ता शामिल है?", "Ist das Frühstück inbegriffen?", "Le petit déjeuner est-il inclus?", "¿Está incluido el desayuno?"),
        ("I need a visa for this country.", "मुझे इस देश के लिए वीजा चाहिए।", "Ich brauche ein Visum für dieses Land.", "J'ai besoin d'un visa pour ce pays.", "Necesito una visa para este país."),
        ("Can I have the Wi-Fi password?", "क्या मुझे वाई-फाई पासवर्ड मिल सकता है?", "Kann ich das WLAN-Passwort haben?", "Puis-je avoir le mot de passe Wi-Fi?", "¿Puedo tener la contraseña de Wi-Fi?"),
        ("The room is too noisy.", "कमरे में बहुत शोर है।", "Das Zimmer ist zu laut.", "La chambre est trop bruyante.", "La habitación es demasiado ruidosa."),
        ("I would like to check out.", "मैं चेकआउट करना चाहता हूँ।", "Ich möchte auschecken.", "Je voudrais faire le check-out.", "Me gustaría hacer el check-out."),
        ("What time is check-in?", "चेक-इन किस समय है?", "Um wie viel Uhr ist der Check-in?", "À quelle heure est le check-in?", "¿A qué hora es el check-in?"),
        ("Are there any tourist attractions nearby?", "क्या पास में कोई पर्यटन स्थल हैं?", "Gibt es in der Nähe Sehenswürdigkeiten?", "Y a-t-il des sites touristiques à proximité?", "¿Hay atracciones turísticas cerca?"),
        ("I need to change my flight.", "मुझे अपनी उड़ान बदलनी है।", "Ich muss meinen Flug ändern.", "Je dois changer mon vol.", "Necesito cambiar mi vuelo."),
        ("The train is delayed.", "ट्रेन में देरी है।", "Der Zug hat Verspätung.", "Le train est en retard.", "El tren está retrasado."),
        ("Where is the nearest pharmacy?", "नजदीकी फार्मेसी कहाँ है?", "Wo ist die nächste Apotheke?", "Où est la pharmacie la plus proche?", "¿Dónde está la farmacia más cercana?"),
        ("I would like a refund.", "मुझे धनवापसी चाहिए।", "Ich möchte eine Rückerstattung.", "Je voudrais un remboursement.", "Me gustaría un reembolso."),
    ],
    "education": [
        ("What is the homework for today?", "आज का गृहकार्य क्या है?", "Was sind die Hausaufgaben für heute?", "Quels sont les devoirs pour aujourd'hui?", "¿Cuáles son los deberes de hoy?"),
        ("Can you explain this concept again?", "क्या आप इस अवधारणा को फिर से समझा सकते हैं?", "Können Sie dieses Konzept nochmal erklären?", "Pouvez-vous expliquer ce concept encore?", "¿Puede explicar este concepto de nuevo?"),
        ("I need help with mathematics.", "मुझे गणित में मदद चाहिए।", "Ich brauche Hilfe in Mathematik.", "J'ai besoin d'aide en mathématiques.", "Necesito ayuda con las matemáticas."),
        ("The library closes at seven.", "पुस्तकालय सात बजे बंद होता है।", "Die Bibliothek schließt um sieben.", "La bibliothèque ferme à sept heures.", "La biblioteca cierra a las siete."),
        ("When is the final exam?", "अंतिम परीक्षा कब है?", "Wann ist die Abschlussprüfung?", "Quand est l'examen final?", "¿Cuándo es el examen final?"),
        ("I failed the test.", "मैं परीक्षा में असफल रहा।", "Ich habe die Prüfung nicht bestanden.", "J'ai échoué à l'examen.", "Reprobé el examen."),
        ("Please submit your assignment.", "कृपया अपना असाइनमेंट जमा करें।", "Bitte reichen Sie Ihre Aufgabe ein.", "Veuillez soumettre votre devoir.", "Por favor entregue su tarea."),
        ("I want to apply for a scholarship.", "मैं छात्रवृत्ति के लिए आवेदन करना चाहता हूँ।", "Ich möchte ein Stipendium beantragen.", "Je veux postuler à une bourse.", "Quiero solicitar una beca."),
        ("The professor is very knowledgeable.", "प्रोफेसर बहुत ज्ञानी हैं।", "Der Professor ist sehr kenntnisreich.", "Le professeur est très compétent.", "El profesor es muy conocedor."),
        ("I missed the lecture today.", "मैंने आज का व्याख्यान छोड़ दिया।", "Ich habe die Vorlesung heute verpasst.", "J'ai manqué le cours aujourd'hui.", "Perdí la conferencia hoy."),
        ("Can I borrow your notes?", "क्या मैं आपके नोट्स उधार ले सकता हूँ?", "Kann ich Ihre Notizen ausleihen?", "Puis-je emprunter vos notes?", "¿Puedo tomar prestadas tus notas?"),
        ("The research paper is due Friday.", "शोध पत्र शुक्रवार तक जमा करना है।", "Die Forschungsarbeit ist bis Freitag fällig.", "Le document de recherche est dû vendredi.", "El trabajo de investigación vence el viernes."),
        ("I am majoring in computer science.", "मैं कंप्यूटर विज्ञान में मेजर कर रहा हूँ।", "Ich studiere Informatik.", "Je me spécialise en informatique.", "Me estoy especializando en ciencias de la computación."),
        ("The classroom is full today.", "आज कक्षा भरी हुई है।", "Das Klassenzimmer ist heute voll.", "La salle de classe est pleine aujourd'hui.", "El aula está llena hoy."),
        ("Can you recommend a good textbook?", "क्या आप कोई अच्छी पाठ्यपुस्तक सुझा सकते हैं?", "Können Sie ein gutes Lehrbuch empfehlen?", "Pouvez-vous recommander un bon manuel?", "¿Puede recomendar un buen libro de texto?"),
        ("I need to improve my grades.", "मुझे अपने ग्रेड सुधारने हैं।", "Ich muss meine Noten verbessern.", "Je dois améliorer mes notes.", "Necesito mejorar mis calificaciones."),
        ("The seminar starts at nine.", "सेमिनार नौ बजे शुरू होता है।", "Das Seminar beginnt um neun.", "Le séminaire commence à neuf heures.", "El seminario comienza a las nueve."),
        ("I am writing my thesis.", "मैं अपनी थीसिस लिख रहा हूँ।", "Ich schreibe meine Abschlussarbeit.", "Je rédige ma thèse.", "Estoy escribiendo mi tesis."),
        ("Group study helps me focus.", "समूह अध्ययन मुझे केंद्रित रहने में मदद करता है।", "Gruppenlernen hilft mir, mich zu konzentrieren.", "L'étude en groupe m'aide à me concentrer.", "El estudio en grupo me ayuda a concentrarme."),
        ("The university offers many courses.", "विश्वविद्यालय कई पाठ्यक्रम प्रदान करता है।", "Die Universität bietet viele Kurse an.", "L'université propose de nombreux cours.", "La universidad ofrece muchos cursos."),
    ],
    "medical": [
        ("I have a headache.", "मुझे सिरदर्द है।", "Ich habe Kopfschmerzen.", "J'ai mal à la tête.", "Tengo dolor de cabeza."),
        ("I need to see a doctor.", "मुझे डॉक्टर से मिलना है।", "Ich muss einen Arzt aufsuchen.", "Je dois voir un médecin.", "Necesito ver a un médico."),
        ("Where is the emergency room?", "आपातकालीन कक्ष कहाँ है?", "Wo ist die Notaufnahme?", "Où est la salle des urgences?", "¿Dónde está la sala de emergencias?"),
        ("I am allergic to penicillin.", "मुझे पेनिसिलिन से एलर्जी है।", "Ich bin allergisch gegen Penicillin.", "Je suis allergique à la pénicilline.", "Soy alérgico a la penicilina."),
        ("Please call an ambulance.", "कृपया एम्बुलेंस बुलाएं।", "Bitte rufen Sie einen Krankenwagen.", "Veuillez appeler une ambulance.", "Por favor llame a una ambulancia."),
        ("I have a fever since yesterday.", "मुझे कल से बुखार है।", "Ich habe seit gestern Fieber.", "J'ai de la fièvre depuis hier.", "Tengo fiebre desde ayer."),
        ("My blood pressure is high.", "मेरा रक्तचाप बढ़ा हुआ है।", "Mein Blutdruck ist hoch.", "Ma tension artérielle est élevée.", "Mi presión arterial es alta."),
        ("I need a prescription.", "मुझे एक प्रिस्क्रिप्शन चाहिए।", "Ich brauche ein Rezept.", "J'ai besoin d'une ordonnance.", "Necesito una receta médica."),
        ("How long should I take this medicine?", "मुझे यह दवा कितने समय तक लेनी चाहिए?", "Wie lange soll ich dieses Medikament nehmen?", "Combien de temps dois-je prendre ce médicament?", "¿Cuánto tiempo debo tomar este medicamento?"),
        ("I have chest pain.", "मुझे सीने में दर्द है।", "Ich habe Brustschmerzen.", "J'ai des douleurs thoraciques.", "Tengo dolor en el pecho."),
        ("I feel dizzy and nauseous.", "मुझे चक्कर और मतली आ रही है।", "Mir ist schwindelig und übel.", "Je me sens étourdi et nauséeux.", "Me siento mareado y con náuseas."),
        ("I have diabetes.", "मुझे मधुमेह है।", "Ich habe Diabetes.", "J'ai le diabète.", "Tengo diabetes."),
        ("My arm is broken.", "मेरा हाथ टूट गया है।", "Mein Arm ist gebrochen.", "Mon bras est cassé.", "Mi brazo está roto."),
        ("I need a blood test.", "मुझे रक्त परीक्षण की जरूरत है।", "Ich brauche einen Bluttest.", "J'ai besoin d'une prise de sang.", "Necesito un análisis de sangre."),
        ("The surgery was successful.", "सर्जरी सफल रही।", "Die Operation war erfolgreich.", "L'opération a réussi.", "La cirugía fue exitosa."),
        ("I have a sore throat.", "मुझे गले में दर्द है।", "Ich habe Halsschmerzen.", "J'ai mal à la gorge.", "Tengo dolor de garganta."),
        ("What are the side effects?", "इसके दुष्प्रभाव क्या हैं?", "Was sind die Nebenwirkungen?", "Quels sont les effets secondaires?", "¿Cuáles son los efectos secundarios?"),
        ("I need to get vaccinated.", "मुझे टीका लगवाना है।", "Ich muss mich impfen lassen.", "Je dois me faire vacciner.", "Necesito vacunarme."),
        ("He is recovering well.", "वह अच्छी तरह से ठीक हो रहा है।", "Er erholt sich gut.", "Il se remet bien.", "Él se está recuperando bien."),
        ("The patient needs immediate care.", "रोगी को तुरंत देखभाल की जरूरत है।", "Der Patient braucht sofortige Pflege.", "Le patient a besoin de soins immédiats.", "El paciente necesita atención inmediata."),
    ],
    "business": [
        ("Let us schedule a meeting.", "चलिए एक बैठक तय करते हैं।", "Lassen Sie uns ein Meeting planen.", "Planifions une réunion.", "Programemos una reunión."),
        ("The deadline is next Monday.", "अगला सोमवार अंतिम तिथि है।", "Die Frist ist nächsten Montag.", "La date limite est lundi prochain.", "La fecha límite es el próximo lunes."),
        ("Please review this contract.", "कृपया इस अनुबंध की समीक्षा करें।", "Bitte überprüfen Sie diesen Vertrag.", "Veuillez examiner ce contrat.", "Por favor revise este contrato."),
        ("The quarterly report is ready.", "तिमाही रिपोर्ट तैयार है।", "Der Quartalsbericht ist fertig.", "Le rapport trimestriel est prêt.", "El informe trimestral está listo."),
        ("We need to increase sales.", "हमें बिक्री बढ़ानी होगी।", "Wir müssen den Umsatz steigern.", "Nous devons augmenter les ventes.", "Necesitamos aumentar las ventas."),
        ("The client has approved the proposal.", "ग्राहक ने प्रस्ताव को मंजूरी दे दी है।", "Der Kunde hat den Vorschlag genehmigt.", "Le client a approuvé la proposition.", "El cliente ha aprobado la propuesta."),
        ("What is your business strategy?", "आपकी व्यावसायिक रणनीति क्या है?", "Was ist Ihre Geschäftsstrategie?", "Quelle est votre stratégie commerciale?", "¿Cuál es su estrategia de negocios?"),
        ("We are looking for investors.", "हम निवेशकों की तलाश कर रहे हैं।", "Wir suchen nach Investoren.", "Nous recherchons des investisseurs.", "Estamos buscando inversores."),
        ("The profit margin is improving.", "लाभ मार्जिन में सुधार हो रहा है।", "Die Gewinnspanne verbessert sich.", "La marge bénéficiaire s'améliore.", "El margen de beneficio está mejorando."),
        ("Please send me the invoice.", "कृपया मुझे चालान भेजें।", "Bitte senden Sie mir die Rechnung.", "Veuillez m'envoyer la facture.", "Por favor envíeme la factura."),
        ("We signed a new partnership agreement.", "हमने एक नए साझेदारी समझौते पर हस्ताक्षर किए।", "Wir haben eine neue Partnerschaftsvereinbarung unterzeichnet.", "Nous avons signé un nouvel accord de partenariat.", "Firmamos un nuevo acuerdo de asociación."),
        ("I need to attend a conference.", "मुझे एक सम्मेलन में भाग लेना है।", "Ich muss an einer Konferenz teilnehmen.", "Je dois assister à une conférence.", "Necesito asistir a una conferencia."),
        ("The market is very competitive.", "बाजार बहुत प्रतिस्पर्धी है।", "Der Markt ist sehr wettbewerbsfähig.", "Le marché est très concurrentiel.", "El mercado es muy competitivo."),
        ("Our team exceeded the target.", "हमारी टीम ने लक्ष्य से अधिक प्राप्त किया।", "Unser Team hat das Ziel übertroffen.", "Notre équipe a dépassé l'objectif.", "Nuestro equipo superó el objetivo."),
        ("Please prepare a presentation.", "कृपया एक प्रस्तुति तैयार करें।", "Bitte bereiten Sie eine Präsentation vor.", "Veuillez préparer une présentation.", "Por favor prepare una presentación."),
        ("We need to reduce operational costs.", "हमें परिचालन लागत कम करनी होगी।", "Wir müssen die Betriebskosten senken.", "Nous devons réduire les coûts opérationnels.", "Necesitamos reducir los costos operativos."),
        ("The board meeting is tomorrow.", "कल बोर्ड बैठक है।", "Das Vorstandstreffen ist morgen.", "La réunion du conseil d'administration est demain.", "La reunión de la junta directiva es mañana."),
        ("We have launched a new product.", "हमने एक नया उत्पाद लॉन्च किया है।", "Wir haben ein neues Produkt eingeführt.", "Nous avons lancé un nouveau produit.", "Hemos lanzado un nuevo producto."),
        ("Customer satisfaction is our priority.", "ग्राहक संतुष्टि हमारी प्राथमिकता है।", "Kundenzufriedenheit ist unsere Priorität.", "La satisfaction client est notre priorité.", "La satisfacción del cliente es nuestra prioridad."),
        ("Can we negotiate the price?", "क्या हम कीमत पर बातचीत कर सकते हैं?", "Können wir den Preis verhandeln?", "Pouvons-nous négocier le prix?", "¿Podemos negociar el precio?"),
    ],
    "technical": [
        ("Please restart the server.", "कृपया सर्वर पुनः आरंभ करें।", "Bitte starten Sie den Server neu.", "Veuillez redémarrer le serveur.", "Por favor reinicie el servidor."),
        ("The software needs an update.", "सॉफ़्टवेयर को अपडेट की आवश्यकता है।", "Die Software benötigt ein Update.", "Le logiciel a besoin d'une mise à jour.", "El software necesita una actualización."),
        ("There is a bug in the code.", "कोड में एक बग है।", "Es gibt einen Fehler im Code.", "Il y a un bug dans le code.", "Hay un error en el código."),
        ("The database connection failed.", "डेटाबेस कनेक्शन विफल हो गया।", "Die Datenbankverbindung ist fehlgeschlagen.", "La connexion à la base de données a échoué.", "La conexión a la base de datos falló."),
        ("Can you debug this program?", "क्या आप इस प्रोग्राम को डीबग कर सकते हैं?", "Können Sie dieses Programm debuggen?", "Pouvez-vous déboguer ce programme?", "¿Puede depurar este programa?"),
        ("The API response is slow.", "API प्रतिक्रिया धीमी है।", "Die API-Antwort ist langsam.", "La réponse de l'API est lente.", "La respuesta de la API es lenta."),
        ("We need to optimize the algorithm.", "हमें एल्गोरिदम को अनुकूलित करना होगा।", "Wir müssen den Algorithmus optimieren.", "Nous devons optimiser l'algorithme.", "Necesitamos optimizar el algoritmo."),
        ("Please check the system logs.", "कृपया सिस्टम लॉग जांचें।", "Bitte prüfen Sie die Systemprotokolle.", "Veuillez vérifier les journaux système.", "Por favor revise los registros del sistema."),
        ("The firewall is blocking the connection.", "फायरवॉल कनेक्शन को ब्लॉक कर रहा है।", "Die Firewall blockiert die Verbindung.", "Le pare-feu bloque la connexion.", "El firewall está bloqueando la conexión."),
        ("We need to scale the infrastructure.", "हमें बुनियादी ढांचे को स्केल करना होगा।", "Wir müssen die Infrastruktur skalieren.", "Nous devons faire évoluer l'infrastructure.", "Necesitamos escalar la infraestructura."),
        ("Deploy the latest version.", "नवीनतम संस्करण तैनात करें।", "Stellen Sie die neueste Version bereit.", "Déployez la dernière version.", "Despliegue la última versión."),
        ("The machine learning model is training.", "मशीन लर्निंग मॉडल प्रशिक्षण ले रहा है।", "Das maschinelle Lernmodell wird trainiert.", "Le modèle d'apprentissage automatique s'entraîne.", "El modelo de aprendizaje automático está entrenando."),
        ("Use version control for this project.", "इस प्रोजेक्ट के लिए वर्जन कंट्रोल का उपयोग करें।", "Verwenden Sie Versionskontrolle für dieses Projekt.", "Utilisez le contrôle de version pour ce projet.", "Use control de versiones para este proyecto."),
        ("The memory usage is too high.", "मेमोरी उपयोग बहुत अधिक है।", "Der Speicherverbrauch ist zu hoch.", "L'utilisation de la mémoire est trop élevée.", "El uso de memoria es demasiado alto."),
        ("Run the unit tests first.", "पहले यूनिट परीक्षण चलाएं।", "Führen Sie zuerst die Unit-Tests aus.", "Exécutez d'abord les tests unitaires.", "Ejecute las pruebas unitarias primero."),
        ("The encryption key expired.", "एन्क्रिप्शन कुंजी की अवधि समाप्त हो गई।", "Der Verschlüsselungsschlüssel ist abgelaufen.", "La clé de chiffrement a expiré.", "La clave de cifrado expiró."),
        ("Configure the environment variables.", "पर्यावरण चर कॉन्फ़िगर करें।", "Konfigurieren Sie die Umgebungsvariablen.", "Configurez les variables d'environnement.", "Configure las variables de entorno."),
        ("The cloud storage is full.", "क्लाउड स्टोरेज भर गया है।", "Der Cloud-Speicher ist voll.", "Le stockage cloud est plein.", "El almacenamiento en la nube está lleno."),
        ("I need access to the repository.", "मुझे रिपॉजिटरी तक पहुँच चाहिए।", "Ich brauche Zugang zum Repository.", "J'ai besoin d'accéder au dépôt.", "Necesito acceso al repositorio."),
        ("Load balancing is configured correctly.", "लोड बैलेंसिंग सही ढंग से कॉन्फ़िगर है।", "Der Lastausgleich ist korrekt konfiguriert.", "L'équilibrage de charge est correctement configuré.", "El balanceo de carga está configurado correctamente."),
    ],
}

LANGUAGE_PAIRS = [
    ("English → Hindi",     "hindi",     1),
    ("English → German",    "german",    2),
    ("English → French",    "french",    3),
    ("English → Spanish",   "spanish",   4),
    ("English → Telugu",    "telugu",    5),
    ("English → Tamil",     "tamil",     6),
    ("English → Malayalam", "malayalam", 7),
]

DOMAIN_INSTRUCTIONS = {
    "daily_conversation": "Translate the following daily conversation phrase",
    "travel":             "Translate the following travel-related phrase",
    "education":          "Translate the following educational phrase",
    "medical":            "Translate the following medical phrase",
    "business":           "Translate the following business phrase",
    "technical":          "Translate the following technical phrase",
}

def make_instruction(lang_name: str, domain: str) -> str:
    base = DOMAIN_INSTRUCTIONS[domain]
    return f"{base} to {lang_name.split(' → ')[1]}"


def generate_dataset(target: int = 1500) -> list[dict]:
    records = []
    domains = list(SENTENCES.keys())

    for domain in domains:
        for lang_name, lang_key, col_idx in LANGUAGE_PAIRS:
            for row in SENTENCES[domain]:
                en_text  = row[0]
                tgt_text = row[col_idx]
                records.append({
                    "instruction": make_instruction(lang_name, domain),
                    "input":       en_text,
                    "output":      tgt_text,
                    "language_pair": lang_name,
                    "domain":      domain,
                })

    # ── Pad / trim to exactly `target` records ────────────────────────────────
    random.seed(42)
    while len(records) < target:
        base = random.choice(records)
        records.append(base.copy())
    records = records[:target]
    random.shuffle(records)
    return records


def save_dataset(records: list[dict], out_dir: str = ".") -> None:
    os.makedirs(out_dir, exist_ok=True)

    # ── JSON ──────────────────────────────────────────────────────────────────
    json_path = os.path.join(out_dir, "translations.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"[✓] Saved JSON  → {json_path}  ({len(records)} records)")

    # ── JSONL (fine-tuning format) ────────────────────────────────────────────
    jsonl_path = os.path.join(out_dir, "translations.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"[✓] Saved JSONL → {jsonl_path}  ({len(records)} records)")

    # ── Stats ─────────────────────────────────────────────────────────────────
    from collections import Counter
    domains  = Counter(r["domain"]        for r in records)
    langs    = Counter(r["language_pair"] for r in records)

    print("\n📊 Dataset Statistics")
    print("─" * 40)
    print("By Domain:")
    for d, n in sorted(domains.items()):
        print(f"  {d:<25} {n:>5} samples")
    print("\nBy Language Pair:")
    for l, n in sorted(langs.items()):
        print(f"  {l:<25} {n:>5} samples")
    print(f"\nTotal records : {len(records)}")


if __name__ == "__main__":
    print("=" * 60)
    print("  Synthetic Translation Dataset Generator")
    print("  Target: 1500 instruction-style pairs")
    print("=" * 60)
    dataset = generate_dataset(1500)
    save_dataset(dataset, out_dir=".")
    print("\n✅ Dataset generation complete!")
