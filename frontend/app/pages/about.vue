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
    <NuxtLink to="/">Back to Quiz</NuxtLink> |
    <NuxtLink to="https://ipt-quiz.streamlit.app/">Available Questions</NuxtLink></h3>

    <h1>About</h1>
    <p>
      Developed for TU/e with ❤️ by Jakub Werner -
      <a href="mailto:me@jakubwerner.com">me@jakubwerner.com</a>
    </p>
    <!-- , and
      to prof. Peter Ruijten-Dodoiu for endorsing the app for 0HV30. -->
    <p>
      Thanks to prof. Daniël Lakens for endorsing the idea and his guidance. Also
      special thanks to Tim, Aaravee and Naomi for their help, Eline, Finn and others for their support 😊!<br>
      The app uses questions made by prev. years' students like me and from the official OpenStax book.
    </p>
    <p>
      This is currently not an official part of the TU/e course, just a passion
      project because I really liked it. I am not responsible for any mistakes or
      inaccuracies.
    </p>

    <p>
      <strong>
        The quiz runs a bit worse on Firefox-based browsers, please
        use Chromium-based ones (Brave, Edge, Chrome...) or Safari for the best experience.
      </strong>
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

    <p>
      <strong
        >Can I contribute by adding my own questions? How can I do that?</strong
      >
    </p>
    <p>
      Not right now, sorry! The effort associated with checking their quality
      is quite high, and I don't have the time right now. :(
      <br />
    </p>

    <p><strong>What exactly is this and why does it exist?</strong></p>
    <p>
      It originated as an app for Intro to P&T, and expanded to BRM1, Social &
      Environmental Psychology. Hopefully it will grow further in the future, we are still in talks
      with the University. Let's see.

      <br />I made it as a hobby project out of previous years' student-made
      questions, the dataset was included as part of the course by
      Daniël Lakens.<br />

    </p>

    <p>
      <strong
        >What did it cost to make the app, and how did you pay for the
        hosting?</strong
      >
    </p>
    <p>
      Close to nothing so far! Thanks to Vuetify, the Firebase free tier and
      GitHub Pages & GitHub Actions! I only pay for LLM tokens. If you
      like the project and want to attempt something similar yourself, feel free
      to contact me. In case you're also a student, check out the GitHub Student
      Pack!
      <br />
      Having a personal domain costs around 8 USD per year through Cloudflare, but I just wanted to be fancy :)
    </p>

    <p><strong>How can I contact you?</strong></p>
    <p>
      For any questions or feedback, <a href="mailto:me@jakubwerner.com">me@jakubwerner.com</a> or
      WhatsApp. I've already implemented many suggestions, thanks for them!
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
