Character creation guide
==========================
This guide will help you to create a new character for Tales of Survival. You can see the format 
in which the character is entered in the sample file: **template_character.yml**. The fields 
must also be entered in this format. Below is a guide, which always shows an example at the end.

1. Name
-------

Choose a name that fits:

- Culture/region (e.g., "Miguel Alvarez" vs. "Ethan Cole").
- Time period (old-fashioned vs. modern).
- Tone of the story (gritty realism vs. lighthearted adventure).

**Example prompts:**
- Where did this person grow up?
- What language or culture influenced their name?

2. Age
------

Pick an age that matches their role:

- **Teen**: discovery, rebellion, coming-of-age
- **20s–30s**: growth, responsibility, dreams vs. reality  
- **40+**: experience, regret, stability or midlife change

3. Background
-------------

Life **before the story starts**.

Include:
- Origin (city, country, environment)
- Family/social class 
- Education/profession
- 1–2 key shaping events

4. Description
--------------

**How they appear and behave now**.

Cover:
- Physical details (build, scars, clothes)
- Habits/body language
- Skills in action
- Hint at inner conflict through behavior

5. Positive Trait
-----------------

**One core strength** that:

- Is useful in your story's situation
- Shows in actions
- Sometimes creates small problems

6. Negative Trait
-----------------

**One meaningful flaw** that:

- Causes conflict/danger
- Contrasts with positive trait
- Gets tested repeatedly

7. Summary
----------

**Mini-pitch** in 2–4 sentences:

1. Introduce character
2. Name key strength  
3. Name key weakness
4. Hint at core conflict

Complete Example
----------------

.. code-block:: yaml

  - name: Markus Weber
    age: 34
    background: Trained carpenter, grew up in a small town in Kentucky.
    description: >
        Markus is a practical, down-to-earth man whose hands are marked from working with wood and
        tools. Even before the outbreak, he was someone who preferred to repair something
        rather than buy it new. His craftsmanship makes him a valuable survivor in a
        world of decay—he can improvise quickly and
        build functional tools or barricades from limited resources. But as useful
        as these skills are, Markus also has a serious weakness.
        He is awkward around other people, as he has always found it difficult to
        trust others and work in a team. In dangerous situations, he tends to
        make stubborn decisions, sometimes at the expense of the group.
    pos_trait: Handy (skilled with tools, can perform repairs faster and more efficiently)
    neg_trait: Cowardly (panics when the situation gets dicey, which can make his actions unreliable)
    summary: >
        Markus is a survivor who is torn between his practical talent and his inner
        fears. His greatest strength—his manual dexterity—could save the group. But 
        when the pressure becomes too great, his insecurities could cause everything to 
        fall apart.
