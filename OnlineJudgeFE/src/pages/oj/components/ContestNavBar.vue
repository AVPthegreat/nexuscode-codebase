<template>
  <div id="contest-navbar">
    <Menu :key="isDarkMode ? 'dark' : 'light'" :theme="isDarkMode ? 'dark' : 'light'" mode="horizontal" @on-select="handleMenuSelect" :active-name="activeMenu" class="oj-menu">
      <div class="logo"><span>{{ contestTitle }}</span></div>
      <Menu-item name="contest-details">
        <Icon type="home"></Icon>
        {{$t('m.Overview')}}
      </Menu-item>
      <Menu-item name="contest-announcement-list">
        <Icon type="chatbubble-working"></Icon>
        {{$t('m.Announcements')}}
      </Menu-item>
      <Menu-item name="contest-problem-list">
        <Icon type="ios-photos"></Icon>
        {{$t('m.Problems')}}
      </Menu-item>
      <Menu-item v-if="showSubmissions" name="contest-submission-list">
        <Icon type="navicon-round"></Icon>
        {{$t('m.Submissions')}}
      </Menu-item>
      <Menu-item v-if="showRank" name="contest-rank">
        <Icon type="stats-bars"></Icon>
        {{$t('m.Rankings')}}
      </Menu-item>
      <Menu-item v-if="showAdminHelper" name="acm-helper">
        <Icon type="ios-paw"></Icon>
        {{$t('m.Admin_Helper')}}
      </Menu-item>
      <template v-if="isAdminRole">
        <Submenu name="rank-admin">
          <template slot="title">
            <Icon type="podium"></Icon>
            {{$t('m.Rank')}}
          </template>
          <Menu-item name="/acm-rank">
            {{$t('m.ACM_Rank')}}
          </Menu-item>
          <Menu-item name="/oi-rank">
            {{$t('m.OI_Rank')}}
          </Menu-item>
        </Submenu>
        <Submenu name="about-admin">
          <template slot="title">
            <Icon type="information-circled"></Icon>
            {{$t('m.About')}}
          </template>
          <Menu-item name="/about">
            {{$t('m.Judger')}}
          </Menu-item>
          <Menu-item name="/FAQ">
            {{$t('m.FAQ')}}
          </Menu-item>
        </Submenu>
      </template>
      <div class="user-section">
        <Button type="ghost"
                class="theme-toggle-btn"
                shape="circle"
                @click="toggleTheme"
                :icon="isDarkMode ? 'ios-sunny' : 'ios-moon'"
                :title="isDarkMode ? 'Light Mode' : 'Dark Mode'">
        </Button>
        <Dropdown class="drop-menu" @on-click="handleRoute" placement="bottom" trigger="click">
          <Button type="text" class="drop-menu-title">{{ user.username }}
            <Icon type="arrow-down-b"></Icon>
          </Button>
          <Dropdown-menu slot="list">
            <Dropdown-item name="/user-home">{{$t('m.MyHome')}}</Dropdown-item>
            <Dropdown-item name="/status?myself=1">{{$t('m.MySubmissions')}}</Dropdown-item>
            <Dropdown-item name="/setting/profile">{{$t('m.Settings')}}</Dropdown-item>
            <Dropdown-item v-if="isAdminRole" name="/admin">{{$t('m.Management')}}</Dropdown-item>
            <Dropdown-item divided name="/logout">{{$t('m.Logout')}}</Dropdown-item>
          </Dropdown-menu>
        </Dropdown>
      </div>
    </Menu>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
export default {
  props: {
    contestTitle: String,
    showSubmissions: Boolean,
    showRank: Boolean,
    showAdminHelper: Boolean
  },
  data () {
    return {
      darkModeActive: false
    }
  },
  computed: {
    ...mapGetters(['user', 'isAdminRole']),
    isDarkMode () {
      return this.darkModeActive
    },
    activeMenu () {
      // Highlight current contest subpage
      const name = this.$route.name
      // Return the route name directly to match Menu-item names
      return name || ''
    }
  },
  mounted () {
    // Load theme preference from localStorage on mount
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark-mode')
      document.body.classList.add('dark-mode')
      this.darkModeActive = true
    }
  },
  methods: {
    handleMenuSelect (routeName) {
      // Restrict during contest lock: allow only Problems list and Submissions
      if (this.$store.state.contest && this.$store.state.contest.started) {
        const allowed = ['contest-problem-list', 'contest-submission-list']
        if (!allowed.includes(routeName)) {
          this.$Message.warning('Only Problems and Submissions are available during contest')
          return
        }
      }
      // Handle menu item selection and navigate
      if (routeName.startsWith('/')) {
        // For admin routes like /acm-rank, /oi-rank, etc.
        this.$router.push(routeName)
      } else {
        // For contest routes
        this.$router.push({ name: routeName, params: { contestID: this.$route.params.contestID } })
      }
    },
    handleRoute (route) {
      if (route && route.indexOf('admin') < 0) {
        this.$router.push(route)
      } else {
        window.open('/admin/')
      }
    },
    toggleTheme () {
      const isDark = document.documentElement.classList.contains('dark-mode')
      if (!isDark) {
        document.documentElement.classList.add('dark-mode')
        document.body.classList.add('dark-mode')
        localStorage.setItem('theme', 'dark')
        this.darkModeActive = true
      } else {
        document.documentElement.classList.remove('dark-mode')
        document.body.classList.remove('dark-mode')
        localStorage.setItem('theme', 'light')
        this.darkModeActive = false
      }
    }
  },
  watch: {
    '$route' () {
      // Update active menu on route change
    }
  }
}
</script>

<style scoped lang="less">
 #contest-navbar {
  position: sticky;
  top: 16px;
  left: 0;
  width: 100%;
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 16px;
  margin-bottom: 0px; // Further decrease gap below navbar

  .oj-menu {
    max-width: 1200px;
    width: 100%;
    background: rgba(252, 252, 252, 0.8);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 9999px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  padding: 8px 24px;
    transition: all 0.3s ease;
    will-change: transform;
    transform: translateZ(0);
    backface-visibility: hidden;
    perspective: 1000px;
    display: flex !important;
    align-items: center;
    height: auto;
    line-height: normal;
    overflow: visible;
    &:hover {
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
  }

  .logo {
    margin-right: 32px;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.05em;
    line-height: 48px;
    color: #e78a53;
    flex-shrink: 0;
    span {
      background: linear-gradient(135deg, #e78a53 0%, #d4693f 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }

  .drop-menu {
    margin-left: auto;
    position: relative;
    flex-shrink: 0;
    &-title {
      font-size: 14px;
      font-weight: 500;
      padding: 6px 16px;
      border-radius: 8px;
      border: 1px solid rgba(0, 0, 0, 0.08);
      background: rgba(255, 255, 255, 0.6);
      backdrop-filter: blur(12px);
      transition: all 0.2s ease;
      &:hover {
        background: rgba(255, 255, 255, 0.9);
        border-color: rgba(0, 0, 0, 0.12);
      }
    }
  }

  .user-section {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  .theme-toggle-btn {
    margin-left: 0;
    transition: all 0.2s ease;
    flex-shrink: 0;
    &:hover {
      transform: translateY(-1px);
    }
  }

  // Menu item styles
  :deep(.ivu-menu-item),
  :deep(.ivu-menu-submenu-title) {
    font-size: 14px;
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 12px;
    transition: all 0.2s ease;
    color: rgba(0, 0, 0, 0.6);
    float: none !important;
    display: inline-flex;
    align-items: center;
    line-height: normal;
    height: auto;
    text-transform: uppercase; // uppercase navbar menu text
    border-bottom: 2px solid transparent;
    &:hover {
      background: rgba(0, 0, 0, 0.04);
      color: rgba(0, 0, 0, 0.9);
      border-bottom-color: #ffffff !important;
    }
    .ivu-icon {
      margin-right: 6px;
      font-size: 16px;
    }
  }

  :deep(.ivu-menu-item-active),
  :deep(.ivu-menu-item-selected) {
    background: rgba(231, 138, 83, 0.1);
    color: #e78a53;
    border-bottom: none !important;
    &:after {
      display: none !important;
    }
    &:before {
      display: none !important;
    }
  }

  :deep(.ivu-menu-horizontal) {
    border-bottom: none !important;
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    height: auto;
    line-height: normal;
    &:after {
      display: none !important;
    }
    &:before {
      display: none !important;
    }
    .ivu-menu-item,
    .ivu-menu-submenu {
      float: none;
      position: relative;
      border-bottom: none !important;
      &:after {
        display: none !important;
      }
    }
  }

  :deep(.ivu-menu-submenu) {
    float: none !important;
    display: inline-block;
  }

  // Dropdown menu styling
  :deep(.ivu-select-dropdown),
  :deep(.ivu-dropdown-menu) {
    border-radius: 12px;
    border: 1px solid rgba(0, 0, 0, 0.08);
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    margin-top: 8px;
    z-index: 10000 !important;
  }
  :deep(.ivu-dropdown) {
    z-index: 10000 !important;
  }
  :deep(.ivu-select-dropdown) {
    z-index: 10000 !important;
  }
  :deep(.ivu-dropdown-item) {
    font-size: 14px;
    padding: 10px 16px;
    transition: all 0.2s ease;
    &:hover {
      background: rgba(0, 0, 0, 0.04);
      color: rgba(0, 0, 0, 0.9);
    }
  }

  // Dark mode adjustments
  :global(.dark-mode) #contest-navbar {
    .oj-menu {
      background: rgba(14, 23, 42, 0.8) !important;
      border-color: rgba(255, 255, 255, 0.1);
    }
    :deep(.ivu-menu-horizontal) {
      background: rgba(14, 23, 42, 0.8) !important;
    }
    :deep(.ivu-menu-dark) {
      background: rgba(14, 23, 42, 0.8) !important;
    }
    :deep(.ivu-menu.ivu-menu-dark.ivu-menu-horizontal) {
      background: rgba(14, 23, 42, 0.8) !important;
    }
    .logo {
      color: #e78a53;
      
      span {
        background: linear-gradient(135deg, #e78a53 0%, #d4693f 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
    }
    .drop-menu-title {
      background: rgba(12, 18, 34, 0.8);
      border-color: rgba(255, 255, 255, 0.1);
      color: #ffffff !important;
      &:hover {
        background: rgba(12, 18, 34, 0.95);
        color: #ffffff !important;
      }
    }
    :deep(.ivu-menu-item),
    :deep(.ivu-menu-submenu-title) {
      color: #ffffff !important;
      &:hover {
        background: rgba(255, 255, 255, 0.08);
        color: #ffffff !important;
      }
    }
    :deep(.ivu-menu-item-active),
    :deep(.ivu-menu-item-selected) {
      background: rgba(231, 138, 83, 0.2);
      color: #ffffff !important;
    }
    :deep(.ivu-select-dropdown),
    :deep(.ivu-dropdown-menu) {
      background: rgba(15, 23, 42, 0.95);
      border-color: rgba(255, 255, 255, 0.1);
    }
    :deep(.ivu-dropdown-item) {
      color: #ffffff !important;
      &:hover {
        background: rgba(255, 255, 255, 0.08);
        color: #ffffff !important;
      }
    }
    .theme-toggle-btn {
      color: #ffffff !important;
      border-color: rgba(255, 255, 255, 0.1);
      &:hover {
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.2);
      }
    }
  }
}
</style>

<style lang="less">
// Unscoped styles to override iView Menu dark theme background
.dark-mode #contest-navbar {
  .ivu-menu-dark,
  .ivu-menu-horizontal.ivu-menu-dark,
  .oj-menu.ivu-menu-dark {
    background: rgba(14, 23, 42, 0.8) !important;
  }
  
  .drop-menu-title {
    background: rgba(12, 18, 34, 0.8) !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
    
    &:hover {
      background: rgba(12, 18, 34, 0.95) !important;
    }
  }
}

/* Force uppercase for all contest navbar menu items */
#contest-navbar .ivu-menu-item,
#contest-navbar .ivu-menu-submenu-title {
  text-transform: uppercase !important;
}

/* Force white text in dark mode for contest navbar */
.dark-mode #contest-navbar .ivu-menu-item,
.dark-mode #contest-navbar .ivu-menu-submenu-title,
.dark-mode #contest-navbar .ivu-menu-item span,
.dark-mode #contest-navbar .ivu-menu-submenu-title span,
.dark-mode #contest-navbar .drop-menu-title,
.dark-mode #contest-navbar .drop-menu-title span,
.dark-mode #contest-navbar .ivu-dropdown-item,
.dark-mode #contest-navbar .theme-toggle-btn,
.dark-mode #contest-navbar .ivu-menu-item *,
.dark-mode #contest-navbar .ivu-menu-submenu-title *,
.dark-mode #contest-navbar .ivu-icon {
  color: #ffffff !important;
}

/* Override iView's default #BFC3CA color in dark mode */
.dark-mode #contest-navbar * {
  color: #ffffff !important;
}

.dark-mode #contest-navbar .ivu-menu {
  color: #ffffff !important;
}

.dark-mode #contest-navbar .ivu-menu-dark .ivu-menu-item,
.dark-mode #contest-navbar .ivu-menu-dark .ivu-menu-submenu-title {
  color: #ffffff !important;
}
</style>

