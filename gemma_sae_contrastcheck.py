print("""HYPOTHESIS (stated before checking): THE CONTRAST SET DETERMINES THE
ABSTRACTION LEVEL OF THE FEATURE MY METHOD FINDS. Not the model -- my design.

  PARIS selection contrasts : Colosseum(IT) / Shibuya(JP) / Brandenburg(DE)
      -> ALL non-French. A FRENCH-LANGUAGE feature is silent for all three,
         so it SURVIVES selection. Result: I found a LANGUAGE feature.

  ZURICH selection contrasts: largest city in AUSTRIA / in GERMANY / in FRANCE
      -> Austria and Germany are GERMAN-SPEAKING. A German-language feature
         would FIRE for them, so it is EXCLUDED. Only a SWITZERLAND feature
         survives. Result: I found a COUNTRY feature.

If that's right, the 'granularity varies by feature' story is wrong. The
granularity varied because MY CONTRASTS VARIED, and I never controlled it.

PREDICTION: re-run PARIS selection with SAME-LANGUAGE contrasts (Montreal,
Dakar, Brussels) and the surviving feature should be FRANCE-bounded, not
francophone -- i.e. it should go SILENT for Montreal.""")
