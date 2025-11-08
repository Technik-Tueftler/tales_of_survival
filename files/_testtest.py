story_type = ("Ereignis", "Erzählung") # Trägt Mod/Overlord nichts in das Test-Modal ein, kommt das Insp. Wort, wenn er was einträgt, wird es so übernommen
# Test 1
output_1 = "Louisville war nur noch ein Schatten seiner selbst. Zerbrochene Scheiben, der Geruch von Verfall und die ständige, flüsternde Drohung der Untoten. Noah, ein Mann mit harten Zügen, suchte in den Trümmern eines Supermarktes nach brauchbaren Dingen, als er einen leisen Schrei hörte. Aus einer Seitengasse stolperte Lena, jung und wildentschlossen, dicht gefolgt von einem Röcheln. Fast gleichzeitig tauchte Elara auf, eine ehemalige Bibliothekarin, deren scharfer Blick die Situation sofort erfasste. Dann kam Jax angerannt, ein geborener Draufgänger, der eine kleine Horde auf den Hals hatte. Ein kurzer, brutaler Kampf brach aus. Noah schlug zu, Lena stach, Elara dirigierte sie in eine enge Gasse, und Jax verteidigte ihren Rücken. Als die letzten Schlurfer fielen und die Stille zurückkehrte, sahen sie sich an – vier Fremde, deren Überleben gerade voneinander abgehangen hatte. „Allein hat man keine Chance mehr“, sagte Noah heiser. Elara nickte. „Zusammen... könnten wir es vielleicht schaffen.“ Lena und Jax tauschten Blicke, ein stummes Einverständnis. Die Gemeinde Louisville hatte gerade ihre ersten vier Mitglieder gefunden."
output_2 = "Die neu gefundene Gemeinschaft zog sich in ein verlassenes Lagerhaus am Rande der Innenstadt zurück. Die erste Aufgabe: die Sicherheit. Jax sicherte die Zugänge, Lena durchsuchte die Regale nach Essbarem und Medkits, während Elara versuchte, eine Übersicht über die wenigen verbliebenen Karten und Pläne der Stadt zu bekommen. Noah schien abwesend. Er saß abseits, eine vergilbte Familienfotografie in den Händen, die er in seiner Tasche gefunden hatte – seine Frau, seine Tochter, lachend, vor der Apokalypse. Ein tiefer Stich der Trauer durchfuhr ihn. Er hatte sie verloren, irgendwo, irgendwie, in diesem Chaos. Der Gedanke, sie im Stich gelassen zu haben, nagte an ihm, selbst als er wusste, er hatte alles versucht. Später am Abend, bei einem kargen Mahl, teilte Elara ihre ersten Erkenntnisse: „Wir brauchen eine Basis, Wasserfilter und vor allem einen Plan.“ Jax grinste: „Klingt nach Arbeit.“ Lena nickte ernst. Noah blickte von seinem Essen auf. Seine Augen waren rot, aber seine Stimme fest: „Gut. Dann fangen wir an zu arbeiten.“ Der Schmerz blieb, aber die Notwendigkeit zu überleben war stärker."
output_3 = 'Wir zogen uns in ein verlassenes Lagerhaus am Rande Louisvilles zurück. Während Jax sich um die Türen kümmerte und Lena eilig Regale nach Vorräten durchsuchte, verschwand ich in meinen eigenen Gedanken. Meine Hand fand wie von selbst die vergilbte Familienfotografie in meiner Tasche. Meine Frau, meine Tochter. Ihr Lachen hallte in meinem Kopf wider, das Geräusch einer Welt, die es nicht mehr gab. Ein eiskalter Stich der Trauer durchfuhr mich. Ich hatte sie verloren, irgendwo, irgendwie, in diesem gottverdammten Chaos. Der Gedanke, sie im Stich gelassen zu haben, nagte an mir, eine endlose Qual, auch wenn ich wusste, ich hatte alles versucht, bis ich nicht mehr konnte. Ich spürte kaum, wie die anderen sich versammelten. Erst als Elara von "Plänen" sprach, blickte ich von meinem kargen Essen auf. Meine Augen waren rot, meine Kehle trocken, aber ich zwang meine Stimme fest zu klingen: „Gut. Dann fangen wir an zu arbeiten.“ Der Schmerz saß tief, er würde bleiben, doch die bloße Notwendigkeit zu überleben drängte sich wie eine Mauer vor meine Trauer.'
# Test 1.5
input_1a = "Du schreibst eine Geschichte mit dem genre Zombie Apokalypse. Die Antworten nur in deutsch. die atmosphere ist düster und der Erzählstil ist Epistolare Roman. Erzähl mir den start einer geschichte (maximal 200 Wörter) bei der sich 4 Charaktere in einer Stadt namens Louisville treffen und beschließen eine gemeinschaft zu bilden."
output_1a = "Die Stadt ist ein Grab, und wir sind die letzten Würmer, die sich in ihrem modrigen Fleisch winden. " \
"Seit Wochen bin ich ein Geist in diesem Leichenhaus, immer kurz vor dem Erstickungstod durch die " \
"allgegenwärtige Verwesung. Heute, zwischen den zerborstenen Fenstern der Main Street, " \
"geschah das Unfassbare. Zuerst Mara, ein Schatten mit einem Gewehr, ihre Augen so " \
"tot wie die der Verdammten. Dann Leo, keuchend aus einer Seitenstraße stolpernd, " \
"sein Gesicht eine Maske aus Angst und Dreck. Und schließlich, aus dem Dunkel eines " \
"eingestürzten Buchladens, Sarah – jung, aber mit einer Kälte, die man nur nach dem " \
"Verlust alles Menschlichen entwickelt. Vier Fremde, vereint durch das Nichts. Wir " \
"saßen im Staub, die ferne Stöhnen der Kreaturen drang durch die zerschlagenen " \
"Scheiben. Keine großen Reden. Nur der unausgesprochene Befehl des Überlebens. " \
"Ein Nicken, ein stummer Konsens. Wir sind eine Gruppe. Eine erbärmliche, vielleicht " \
"kurzlebige Gemeinschaft in den sterbenden Adern Louisvilles. Wohin, weiß der Teufel. " \
"Aber ich habe meinen Namen nicht genannt. Sie auch nicht. Morgen vielleicht. Wenn es ein Morgen gibt."
# Test 2
output_21 = """**October 17th, 20XX**  **Location:** Louisville – Abandoned Barber Shop, Bardstown Road The ink bleeds a little, just like everything else these days. I barely made it through the last block, the air thick with that metallic sweetness I’ve come to dread. And then, here. Four of us. An unlikely collection of wreckage. There’s Elias, a bear of a man, his face a roadmap of exhaustion, already securing the door with a rusted filing cabinet. He was here first, apparently. Then Clara, no older than my niece would be, silent and unnerving, her eyes constantly scanning the street through a gap in the boarded-up window. She carries a claw hammer like it’s an extension of her arm. The last to arrive was Finn. He stumbled in, muttering about 'the silence before the scream,' clutching a bottle of antiseptic as if it were a holy relic. He seems to be perpetually on the verge of laughter or tears. We didn’t talk much, just exchanged wary glances, the kind that ask, "Are you more dangerous than *them*?" But when Elias finally spoke, his voice gravelly, "We either tie our ropes together, or we drown alone," no one argued. Clara gave a curt nod. Finn just stared at his hands, then at us. A community. Born of fear, forged in ash. God help us."""
output_22 = """
**October 19th, 20XX** **Location:** Louisville – Abandoned Barber Shop, Bardstown Road

The silence is shattered not by the moan of the dead, but by Elias’s choked cry. We were foolish, venturing out so soon, trusting the deceptive calm of a fog-laden morning to fetch water from a nearby deli. A trip wire, old and rusted, tripped him. He fell hard, his leg twisting beneath him, a sickening crack echoing through the empty street. Now, back in our makeshift sanctuary, his breath comes in ragged gasps. The wound isn’t deep, but the ankle is a swollen, purple mess.

Finn, surprisingly, is the one with steady hands, carefully cleaning the abrasions with his precious antiseptic. Clara stands guard, her silhouette stark against the boarded window, eyes fixed on the street. No one speaks of the irony, of how quickly our nascent "community" is crippled. Elias, the one who urged us to tie our ropes together, is now the anchor threatening to drag us down. A grim weight settles over us. We are one less pair of strong legs, one more mouth to feed, one more reason for despair to creep into the 
corners of our minds. The rope feels thinner than ever.
"""
# Test 3
"""**Logbucheintrag #78**
**Datum:** 27. Oktober – Jahr Eins der Stille.
**Ort:** Louisville, Kentucky. Ehemaliges Industriegebiet, Sektor B-17.

Die Ruinen dieser einst so lebhaften Stadt sind ein Friedhof, umspült von den Schatten der 
Lebenden und der Toten. Die Luft ist schwer vom Geruch des Verfalls, durchsetzt mit einem 
Hauch von Hoffnung – oder dem Wahnsinn, den man dafür halten mag. Heute, inmitten dieses 
Graus, hat sich eine Ansammlung von Seelen gefunden, gezwungen durch die unerbittliche Leere, 
einen fragilen Pakt zu schmieden.

Ich habe sie beobachtet, wie sie sich in der verlassenen Montagehalle zusammenfanden, jeder 
ein Splitter einer zerbrochenen Welt.

Da war **Markus**. Seine Hände, schwielig und rau wie altes Eichenholz, arbeiteten an einem 
provisorischen Bolzenriegel für eine rostige Eisentür. Er murmelte mehr zu sich selbst als zu 
den anderen, während er Metall auf Metall schlug. Er sprach kaum, 
doch seine Bewegungen waren präzise, effizient. Als Lena mit einer alten Kanisterlampe ankam, 
die flackerte und zu verlöschen 
drohte, riss Markus sie ihr förmlich aus der Hand, zückte ein Werkzeug und begann zu fummeln. 
Misstrauen stand ihm ins Gesicht geschrieben, als ob jede Hilfe, jeder Blick eine List sei. 
Er war ein Solitär, gefangen in der Notwendigkeit der Gruppe. „Verschwende keine Ressourcen“, 
knurrte er, ohne aufzublicken.

**Anna** saß abseits, ihre Bewegungen waren so ruhig wie die eines Uhrmachers. Mit antiseptischen 
Tüchern reinigte sie sorgfältig eine Schnittwunde an Joachims Arm. Ihre Finger waren geübt, fast 
zärtlich, doch ihre Stirn war in Falten gelegt, als ob sie jede mögliche Komplikation vorwegnehmen 
wollte. „Wir brauchen mehr Verbandszeug“, sagte sie leise, ihre Stimme klang wie ein sanfter 
Vorwurf an die Welt. Ihre Besonnenheit war ein Anker, doch ich sah, wie sie zögerte, als Joachim 
forderte, die Tür sofort zu verschließen, ohne auf Lena zu warten.

**Joachim**, ein Koloss aus Muskeln und rohem Willen, war die treibende Kraft. Er hatte die Halle 
quasi im Alleingang von den 
„Wanderern“ befreit, wie er sie nannte. Sein Atem ging noch immer schwer, die Axt, die er schwang, 
war blutverschmiert. „Wir können nicht ewig hier sitzen und warten“, brüllte er in die Runde, 
seine Augen scannten die Schatten, immer auf der Hut. „Wir 
müssen einen Plan haben, eine Strategie. Oder wir sind nur Futter.“ Seine Impulsivität war spürbar, 
eine Flamme, die zu schnell brennen konnte, aber in dieser Finsternis war sie auch ein Leitstern.

Und dann war da **Lena**. Sie huschte zurück in die Halle, ihre Schritte so leicht, dass man sie 
kaum hörte. In ihren Armen trug sie eine Kiste mit Konserven und eine verstaubte Karte. Sie hatte 
die stillen Gassen und die verborgenen Eingänge genutzt, 
um sich ungesehen zu bewegen. Ihre Augen, wachsam und neugierig, fixierten jeden Winkel des Raumes, 
als ob sie die unsichtbaren Fallen und Möglichkeiten scannen würde. „Oben, in den Büros, gibt es 
noch mehr“, flüsterte sie, ihre Stimme kaum hörbar. Eine Waghalsigkeit, die wertvoll war, aber auch 
ein gefährlicher Tanz am Abgrund.

Die Entscheidung fiel nicht leicht. Markus knurrte, Anna zögerte, Joachim hämmerte auf den Tisch, 
und Lena lauschte den Geräuschen draußen. Doch der Hunger, die Kälte und das unaufhörliche Stöhnen 
von draußen waren mächtigere Argumente als jeder Zweifel. „Allein sind wir tot“, sagte Anna schließlich, 
ihre Stimme fester als erwartet.

Es war eine widerwillige Kapitulation vor der Realität. Vier zerbrochene Seelen, jede mit ihren Narben 
und Gaben, die sich in 
einem gottverlassenen Lagerhaus in Louisville zusammentaten. Nicht aus Zuneigung, sondern aus schierer 
Notwendigkeit. Eine Gemeinschaft, geboren aus Verzweiflung. Mögen die Götter uns gnädig sein. 
Oder was auch immer davon übrig ist."""

"""**Aus einem gefundenen Logbuch, datiert 12. Oktober, Jahr 3 nach dem Fall:**

Die Welt, wie wir sie kannten, ist ein verrottender Leichnam. Was blieb, sind die Knochen unserer Städte, 
überwuchert von stummen Ranken, die sich durch Beton und Stahl fressen, als wollten sie unsere Fehler 
begraben. Die Straßen sind Korridore des Todes, bevölkert von den leeren Hüllen dessen, was einmal 
Menschen waren. Wir leben in den Schatten, jagen nach Konserven, nach einem Tropfen sauberem Wasser, 
nach jeder Kugel, als wäre sie Gold wert. Der Horizont ist nicht länger das Versprechen eines 
neuen Morgens, sondern eine weitere Grenze, hinter der die gleichen Gefahren lauern: die Untoten, 
die Verzweiflung, die andere zu Bestien macht, und die allgegenwärtige Kälte in den Seelen. 
Jede Nacht lauschen wir auf das Knurren in der Ferne, jede Dämmerung ist ein unsicherer Sieg. 
Die Zivilisation ist ein ferner Traum. Nur das Überleben zählt.

***

**Aus Elias' Logbuch, 19. April, Jahr 1 nach dem Fall:**

Louisville. Eine Falle aus Beton und rostigem Metall, wie jede andere Stadt. Ich hatte mich in die Überreste einer Apotheke gewagt, auf der Suche nach Schmerzmitteln – mein Knie pochte wie ein Höllenfeuer nach der letzten Begegnung mit einem Rudel Beißer. Der Geruch von Verwesung und modrigem Papier hing schwer in der Luft. Ich war nicht allein.

Ein leises Schaben. Eine junge Frau, kaum älter als zwanzig, huschte zwischen den Regalen hindurch. Zara, wie ich später erfuhr, eine Schattenjägerin, schnell wie ein Wiesel, mit Augen, die mehr gesehen hatten, als jedes Kind je sollte. Sie war dabei, 
eine Kiste Konserven auszuweiden, die ich selbst übersehen hatte. Wir starrten uns an, meine Hand am Griff meines Beils. Misstrauen war die einzige Währung dieser neuen Welt, und es lag dick in der Luft.

Bevor die Spannung eskalieren konnte, hörten wir es: ein schweres Keuchen, das sich näherte. Nicht nur einer. Ein tiefes Knurren, das den Boden unter meinen abgewetzten Stiefeln vibrieren ließ. Eine kleine Horde. Wir brauchten Deckung, schnell.        

Plötzlich durchbrach ein Mann, ein Koloss, die Rückwand der Apotheke. Marcus. Er war gerade dabei, eine provisorische Barrikade aus Schrott und aufgebrochenen Schränken zu errichten, offenbar um einen sicheren Weg nach draußen zu schaffen. Er sah uns, 
nickte nur kurz und wies mit dem Kinn auf die sich nähernden Schatten vor der Tür – die Beißer.

Dann kam Lena. Sie war leise, fast unmerklich, und trug eine Tasche, die verdächtig nach medizinischen Vorräten aussah. Eine ehemalige Krankenschwester, mit einer ruhigen Entschlossenheit, die in dieser Hölle selten war. Sie hatte sich bei dem Lärm der Untoten versteckt und war uns nun in die Falle gelaufen. Ihr Blick wanderte von mir zu Zara, dann zu Marcus, der bereits die 
ersten Schritte unternahm, um die zerbrochene Eingangstür zu sichern.

Keiner von uns sprach ein Wort, aber die Botschaft war klar: Wir waren zu viert in der Enge, die Untoten klopften an die Tür. 
Einer allein hatte keine Chance. Aber vier? Vier könnten vielleicht überleben, vielleicht sogar eine Flucht wagen.

Wir kämpften. Marcus hielt die Linie mit einem Rohr, das er wie einen Speer schwang, ich deckte ihn mit meiner abgesägten Schrotflinte. Zara huschte wie ein Geist umher, lenkte ab, stach zu, fand die Schwachstellen in den fauligen Körpern. Lena, selbst unter Adrenalin, versorgte meine oberflächliche Wunde, die ich mir beim Zurückweichen geholt hatte, bevor ich es überhaupt bemerkt hatte, und bewahrte uns vor einem fatalen Fehler.

Als die letzte Hülle zu Boden ging und die Stille zurückkehrte, eine zerbrochene, angespannte Stille, sahen wir uns wieder an. Das Misstrauen war nicht verschwunden, aber etwas anderes hatte sich dazugesellt: eine flüchtige, gefährliche Form von Respekt.

„Allein stirbt man schnell“, sagte ich, meine Stimme rau von der Anstrengung.

Lena nickte. „Zusammen hat man eine Chance. Eine kleine, aber immerhin eine.“

Marcus grummelte zustimmend, seine breiten Schultern zuckten. Zara zuckte die Achseln, aber ihre Augen strahlten eine neue Art von Wachsamkeit aus, die weniger von Furcht als von Pragmatismus sprach.

So begann es. Vier Fremde, in den Ruinen von Louisville, gezwungen durch die Umstände, eine Gemeinschaft zu bilden, die vielleicht unser Untergang sein würde, oder unsere einzige Hoffnung. Ich schrieb diesen Eintrag bei flackerndem Licht, das Gefühl, dass wir etwas getan hatten, das die Regeln der neuen Welt herausforderte. Es war ein Risiko, aber was war es nicht?"""