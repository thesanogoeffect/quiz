<template>
  <v-app>
    <v-app-bar color="primary" density="comfortable" flat>
      <v-btn
        icon="mdi-arrow-left"
        variant="text"
        aria-label="Back to the quiz"
        :to="{ name: 'index' }"
      ></v-btn>
      <v-toolbar-title>About</v-toolbar-title>
    </v-app-bar>

    <v-main>
      <v-container class="about">
        <div class="links">
          <a
            href="https://www.buymeacoffee.com/thesanogoeffect"
            target="_blank"
            rel="noopener"
          >
            <img
              src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png"
              alt="Buy Me A Coffee"
              class="icon"
            />
          </a>

          <a
            href="https://www.linkedin.com/in/jakubwerner"
            target="_blank"
            rel="noopener"
            >Connect on LinkedIn</a
          >
        </div>

        <p class="nav-links">
          <NuxtLink :to="{ name: 'index' }">Back to Quiz</NuxtLink> |
          <NuxtLink :to="{ name: 'questions' }">Available Questions</NuxtLink>
        </p>

        <h1>About</h1>
        <p>
          Developed for TU/e with ❤️ by Jakub Werner -
          <a href="mailto:me@jakubwerner.com">me@jakubwerner.com</a>
        </p>
        <p>
          Thanks to prof. Daniël Lakens for endorsing the idea and his guidance.
          Also special thanks to Tim, Aaravee and Naomi for their help, as well as
          to Eline, Finn, Hubert and others for their support 😊!<br />
          The app uses questions made by previous years' students like me and from
          the official OpenStax book.
        </p>
        <p>
          This is currently not an official part of the TU/e course, just a passion
          project because I really liked it. I am not responsible for any mistakes
          or inaccuracies.
        </p>

        <h2>F.A.Q.</h2>

        <p><strong>Can I contribute by adding my own questions?</strong></p>
        <p>
          Not right now, sorry! The effort associated with checking their quality is
          quite high, and I don't have the time. What does help a lot: flagging
          questions that look wrong, and up- or downvoting them.
        </p>

        <p><strong>What exactly is this and why does it exist?</strong></p>
        <p>
          It originated as an app for Intro to P&amp;T, and expanded to BRM1 and
          Social &amp; Environmental Psychology. Hopefully it will grow further -
          we are still in talks with the university. Let's see.
          <br />I made it as a hobby project out of previous years' student-made
          questions; the dataset was included as part of the course by Daniël
          Lakens.
        </p>

        <p>
          <strong>What did it cost to make the app, and how did you pay for the
            hosting?</strong
          >
        </p>
        <p>
          Close to nothing so far! Thanks to Vuetify, the Firebase free tier and
          Cloudflare Pages! I only pay for LLM tokens. If you like
          the project and want to attempt something similar yourself, feel free to
          contact me. In case you're also a student, check out the GitHub Student
          Pack!
          <br />
          Having a personal domain costs around 8 USD per year through Cloudflare,
          but I just wanted to be fancy :)
        </p>

        <p><strong>How can I contact you?</strong></p>
        <p>
          For any questions or feedback,
          <a href="mailto:me@jakubwerner.com">me@jakubwerner.com</a> or WhatsApp.
          I've already implemented many suggestions, thanks for them!
        </p>

        <p><strong>Did you steal the Reddit karma UI?</strong></p>
        <p>If you're from the Reddit legal team, then no, I did not.</p>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
useHead({ title: "About · Intro to P&T Quiz" });
</script>

<style scoped>
.about {
  max-width: 800px;
  padding: 20px;
}

.about h1 {
  font-size: 2em;
  margin-bottom: 10px;
}

.about h2 {
  margin-top: 24px;
  margin-bottom: 10px;
}

.about p {
  font-size: 1.05em;
  line-height: 1.6;
  margin-bottom: 15px;
}

.nav-links {
  font-weight: 600;
}

.links {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.links a {
  display: flex;
  align-items: center;
  text-decoration: none;
  font-size: 1.05em;
}

.links img.icon {
  width: auto;
  height: 48px;
}
</style>
