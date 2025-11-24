<template>
  <div>
    <component :is="isContestRoute ? 'ContestNavBar' : 'NavBar'" v-bind="contestNavBarProps" />
    <div class="content-app">
      <transition name="fadeInUp" mode="out-in">
        <router-view></router-view>
      </transition>
      <div class="footer"></div>
    </div>
    <BackTop></BackTop>
  </div>
</template>

<script>
import { mapActions, mapState, mapGetters } from 'vuex'
import NavBar from '@oj/components/NavBar.vue'
import ContestNavBar from '@oj/components/ContestNavBar.vue'

export default {
  name: 'app',
  components: {
    NavBar,
    ContestNavBar
  },
  data() {
    return {
      version: process.env.VERSION
    }
  },
  created() {
    try {
      document.body.removeChild(document.getElementById('app-loader'))
    } catch (e) {
    }
  },
  mounted() {
    this.getWebsiteConfig()
  },
  methods: {
    ...mapActions(['getWebsiteConfig', 'changeDomTitle'])
  },
  computed: {
    ...mapState(['website']),
    ...mapGetters([
      'contest',
      'OIContestRealTimePermission',
      'isContestAdmin',
      'contestRuleType'
    ]),
    isContestRoute() {
      // Only show ContestNavBar for contest-details and its children, not for contest-list
      const name = this.$route.name
      return name === 'contest-details' || (name && name.startsWith('contest-') && name !== 'contest-list')
    },
    contestNavBarProps() {
      if (!this.isContestRoute) return {}
      return {
        contestTitle: (this.contest && this.contest.title) ? this.contest.title : '',
        showSubmissions: this.OIContestRealTimePermission,
        showRank: this.OIContestRealTimePermission,
        showAdminHelper: this.isContestAdmin && this.contestRuleType === 'ACM'
      }
    }
  },
  watch: {
    'website'() {
      this.changeDomTitle()
    },
    '$route'() {
      this.changeDomTitle()
    }
  }
}
</script>

<style lang="less">
* {
  -webkit-box-sizing: border-box;
  -moz-box-sizing: border-box;
  box-sizing: border-box;
}

body {
  background-color: var(--nexus-bg);
  color: var(--nexus-text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  min-height: 100vh;
}

// Ensure scrolling works in fullscreen mode
html:fullscreen,
html:-webkit-full-screen,
html:-moz-full-screen,
html:-ms-fullscreen {
  overflow: auto !important;
  height: 100%;
}

body:fullscreen,
body:-webkit-full-screen,
body:-moz-full-screen,
body:-ms-fullscreen {
  overflow: auto !important;
  height: 100%;
}

a {
  text-decoration: none;
  background-color: transparent;
  color: var(--nexus-primary);
  transition: var(--nexus-transition);

  &:active,
  &:hover {
    outline-width: 0;
    color: var(--nexus-primary-hover);
  }
}

.content-app {
  padding-top: 100px;
  padding-left: 0;
  padding-right: 0;
  width: 100%;
  margin: 0;
  min-height: calc(100vh - 150px);
}

.footer {
  margin-top: 40px;
  margin-bottom: 20px;
  text-align: center;
  font-size: small;
  color: var(--nexus-text-secondary);
}

.fadeInUp-enter-active {
  animation: fadeInUp .5s;
}
</style>
