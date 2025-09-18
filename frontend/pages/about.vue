<template>
  <div class="about">
    <div class="links">
      <a href="https://www.buymeacoffee.com/thesanogoeffect" target="_blank">
        <img
          src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png"
          alt="Buy Me A Coffee"
          class="icon"
        />
      </a>

      <a href="https://www.linkedin.com/in/jakubwerner" target="_blank">
        <img
          src="https://cdn-icons-png.flaticon.com/512/174/174857.png"
          alt="LinkedIn"
          class="icon"
        />
        Connect on LinkedIn
      </a>
    </div>
    <h3>
    <NuxtLink to="/">Back to Quiz</NuxtLink>
    <NuxtLink to="https://brm-1-questions.streamlit.app/">Available Questions</NuxtLink></h3>

    <br />
    <p>
      Some questions <b>might be incorrect</b> or not good as they were made
      using AI - you can flag them.
      <b>If anything seems weird, please let me know</b>.
    </p>

    <p>
      If you want to contribute by adding your own questions, you can do so
      <a href="https://forms.gle/jqbZyt923NuUbG446" target="_blank"> here</a
      >.<br />
    </p>

    <h1>About</h1>
    <p>
      Developed for TU/e with ❤️ by Jakub Werner -
      <a href="mailto:j.werner@student.tue.nl">j.werner@student.tue.nl</a>
    </p>
    <!-- , and
      to prof. Peter Ruijten-Dodoiu for endorsing the app for 0HV30. -->
    <p>
      Thanks to prof. Daniël Lakens for endorsing the idea and his generous support. Also
      special thanks to Tim, Aaravee and Naomi for their help and Eline and Finn for their support 😊!<br>
      The app uses questions from the Price book and the BRM 1 lecture slides.
    </p>
    <p>
      This is currently not an official part of the TU/e course, just a passion
      project because I really like it. I am not responsible for any mistakes or
      inaccuracies.
    </p>

    <h2>F.A.Q.:</h2>
    <p>
      <strong>
        Why is the scroll bar inside questions invisible on iPhone/iPad and only
        appears after scrolling?
      </strong>
    </p>
    <p>
      This is a known issue with iOS in general, but really sucks here. The
      scrollbar is hidden by default and only appears when you start scrolling.
      Maybe I'll fix it in the future.
    </p>

    <p><strong>What exactly is this and why does it exist?</strong></p>
    <p>
      It originated as an app for Intro to PT:
      <a
        href="https://thesanogoeffect.github.io/intro-psych-quiz/"
        target="_blank"
        >https://thesanogoeffect.github.io/intro-psych-quiz/</a
      >

      <br />I made it as a hobby project out of prev. years' student-made
      questions, had to be made as a part of the course and were shared by
      Daniël Lakens <br />
      People liked the app, so I made a version for this course as well.
      <br />However, there were no questions to use this time, so I used an AI
      RAG system to generate them. I am aware that some of them are not perfect,
      so please flag them if you think so.
    </p>

    <p>
      <strong
        >What did it cost to make the app, and how did you pay for the
        hosting?</strong
      >
    </p>
    <p>
      Nothing so far! Thanks to Vuetify, the generous Firebase free tier, and
      GitHub Pages & GitHub Actions! I only pay for the OpenAI tokens. If you
      like the project and want to attempt something similar yourself, feel free
      to contact me. In case you're also a student, check out the GitHub Student
      Pack!
    </p>

    <p><strong>How can I contact you?</strong></p>
    <p>
      For any questions or feedback, hit me up at <a href="mailto:j.werner@student.tue.nl">j.werner@student.tue.nl</a> or
      WhatsApp. I have already implemented some of your suggestions, thanks for
      that!
    </p>

    <p><strong>Did you steal the Reddit karma UI?</strong></p>
    <p>If you're from the Reddit legal team, then no, I did not</p>
  </div>
</template>

<script>
export default {
  name: "About",
};
</script>

<style scoped>
.about {
  padding: 20px;
}

.about h1 {
  font-size: 2em;
  margin-bottom: 10px;
}

.about p {
  font-size: 1.2em;
  margin-bottom: 15px;
}

.about h2 {
  margin-top: 20px;
  margin-bottom: 10px;
}

.links {
  margin-bottom: 20px;
  display: flex;
  align-items: center; /* Aligns items vertically */
}

.links a {
  display: flex;
  align-items: center;
  margin-right: 15px;
  text-decoration: none;
  font-size: 1.1em;
}

.icon {
  width: 30px;
  height: 30px;
  margin-right: 8px;
  vertical-align: middle;
}

.links img.icon {
  width: auto;
  height: 60px; /* Matches the height of the Buy Me A Coffee button */
}
</style>
