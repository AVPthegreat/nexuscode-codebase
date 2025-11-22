<template>
  <div id="header">
    <Menu theme="light" mode="horizontal" @on-select="handleRoute" :active-name="activeMenu" class="oj-menu">
      <div class="logo"><span>NEXUSCODE</span></div>
      <Menu-item name="/">
        <Icon type="home"></Icon>
        {{ $t('m.Home') }}
      </Menu-item>
      <Menu-item name="/problem">
        <Icon type="ios-keypad"></Icon>
        {{ $t('m.NavProblems') }}
      </Menu-item>
      <Menu-item name="/contest">
        <Icon type="trophy"></Icon>
        {{ $t('m.Contests') }}
      </Menu-item>
      <Menu-item name="/status" :disabled="contestLocked">
        <Icon type="ios-pulse-strong"></Icon>
        {{ $t('m.NavStatus') }}
      </Menu-item>
      <Menu-item name="/discussions" :disabled="contestLocked">
        <Icon type="chatbubble-working"></Icon>
        Discussions
      </Menu-item>
      <template v-if="isAdminRole">
        <Submenu name="rank">
          <template slot="title">
            <Icon type="podium"></Icon>
            {{ $t('m.Rank') }}
          </template>
          <Menu-item name="/acm-rank">
            {{ $t('m.ACM_Rank') }}
          </Menu-item>
          <Menu-item name="/oi-rank">
            {{ $t('m.OI_Rank') }}
          </Menu-item>
        </Submenu>
        <Submenu name="about">
          <template slot="title">
            <Icon type="information-circled"></Icon>
            {{ $t('m.About') }}
          </template>
          <Menu-item name="/about">
            {{ $t('m.Judger') }}
          </Menu-item>
          <Menu-item name="/FAQ">
            {{ $t('m.FAQ') }}
          </Menu-item>
        </Submenu>
      </template>
      <template v-if="!isAuthenticated">
        <div class="btn-menu">
          <Button type="ghost" shape="circle" @click="toggleTheme" :icon="isDarkMode ? 'ios-sunny' : 'ios-moon'"
            style="margin-right: 5px;" :title="isDarkMode ? 'Light Mode' : 'Dark Mode'">
          </Button>
          <Button type="ghost" ref="loginBtn" shape="circle" @click="handleBtnClick('login')">{{ $t('m.Login') }}
          </Button>
          <Button v-if="website.allow_register" type="ghost" shape="circle" @click="handleBtnClick('register')"
            style="margin-left: 5px;">{{ $t('m.Register') }}
          </Button>
        </div>
      </template>
      <template v-else>
        <div class="user-section">
          <Button type="ghost" class="theme-toggle-btn" shape="circle" @click="toggleTheme"
            :icon="isDarkMode ? 'ios-sunny' : 'ios-moon'" :title="isDarkMode ? 'Light Mode' : 'Dark Mode'">
          </Button>
          <Button type="text" class="username-btn" @click="handleRoute('/user-home')">
            {{ user.username }}
          </Button>
        </div>
      </template>
    </Menu>
    <Modal v-model="modalVisible" :width="400">
      <div slot="header" class="modal-title">{{ $t('m.Welcome_to') }} {{ website.website_name_shortcut }}</div>
      <component :is="modalStatus.mode" v-if="modalVisible"></component>
      <div slot="footer" style="display: none"></div>
    </Modal>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import login from '@oj/views/user/Login'
import register from '@oj/views/user/Register'

export default {
  components: {
    login,
    register
  },
  data() {
    return {
      isDarkMode: false
    }
  },
  mounted() {
    this.getProfile()
    // Load theme preference from localStorage
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme === 'dark') {
      this.isDarkMode = true
      document.documentElement.classList.add('dark-mode')
      document.body.classList.add('dark-mode')
    }
  },
  methods: {
    ...mapActions(['getProfile', 'changeModalStatus']),
    handleRoute(route) {
      // Block status and most navigation during active contest
      if (this.$store.state.contest && this.$store.state.contest.started) {
        if (route && route.indexOf('/status') === 0) {
          this.$Message.warning('During the contest, open Submissions from the problem page only.')
          return
        }
        // Allow only staying within contest subtree or homepage
        if (route && !route.startsWith('/contest/')) {
          this.$Message.warning('Contest in progress. Navigation is limited.')
          return
        }
      }
      if (route && route.indexOf('admin') < 0) {
        this.$router.push(route)
      } else {
        window.open('/admin/')
      }
    },
    handleBtnClick(mode) {
      this.changeModalStatus({
        visible: true,
        mode: mode
      })
    },
    toggleTheme() {
      this.isDarkMode = !this.isDarkMode
      if (this.isDarkMode) {
        document.documentElement.classList.add('dark-mode')
        document.body.classList.add('dark-mode')
        localStorage.setItem('theme', 'dark')
      } else {
        document.documentElement.classList.remove('dark-mode')
        document.body.classList.remove('dark-mode')
        localStorage.setItem('theme', 'light')
      }
    }
  },
  computed: {
    ...mapGetters(['website', 'modalStatus', 'user', 'isAuthenticated', 'isAdminRole']),
    // Follow route changes
    activeMenu() {
      return '/' + this.$route.path.split('/')[1]
    },
    contestLocked() {
      return this.$store.state.contest && this.$store.state.contest.started
    },
    modalVisible: {
      get() {
        return this.modalStatus.visible
      },
      set(value) {
        this.changeModalStatus({ visible: value })
      }
    }
  }
}
</script>

<style lang="less" scoped>
#header {
  display: contents;

  .oj-menu {
    position: fixed;
    top: 16px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    max-width: 1200px;
    width: calc(100% - 32px);
    background: var(--nexus-surface);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: var(--nexus-radius-full);
    border: 1px solid var(--nexus-border);
    box-shadow: var(--nexus-shadow-lg);
    padding: 8px 24px;
    transition: var(--nexus-transition);
    display: flex !important;
    align-items: center;
    height: auto;
    line-height: normal;

    &:hover {
      box-shadow: var(--nexus-shadow-lg);
      border-color: var(--nexus-border-hover);
    }
  }

  .logo {
    margin-right: 32px;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.05em;
    line-height: 50px;
    color: var(--nexus-primary);
    flex-shrink: 0;

    span {
      background: linear-gradient(135deg, var(--nexus-primary) 0%, var(--nexus-secondary) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }

  .username-btn {
    font-size: 14px;
    font-weight: 500;
    padding: 6px 16px;
    border-radius: var(--nexus-radius);
    border: 1px solid transparent;
    background: transparent;
    color: var(--nexus-text-primary);
    transition: var(--nexus-transition);

    &:hover {
      background: var(--nexus-surface-hover);
      color: var(--nexus-primary);
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
      border-radius: var(--nexus-radius);
      border: 1px solid transparent;
      background: transparent;
      color: var(--nexus-text-primary);
      transition: var(--nexus-transition);

      &:hover {
        background: var(--nexus-surface-hover);
      }
    }
  }

  .user-section,
  .btn-menu {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  .theme-toggle-btn {
    margin-left: 0;
    transition: var(--nexus-transition);
    color: var(--nexus-text-secondary);

    &:hover {
      color: var(--nexus-accent);
      transform: rotate(15deg);
    }
  }
}

// Menu item styles
:deep(.ivu-menu-item),
:deep(.ivu-menu-submenu-title) {
  font-size: 14px;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: var(--nexus-radius);
  transition: var(--nexus-transition);
  color: var(--nexus-text-secondary);
  float: none !important;
  display: inline-flex;
  align-items: center;
  line-height: 50px;
  height: 50px;
  text-transform: uppercase;
  border-bottom: 2px solid transparent;

  &:hover {
    background: var(--nexus-surface-hover);
    color: var(--nexus-primary);
  }

  .ivu-icon {
    margin-right: 6px;
    font-size: 18px;
  }
}

:deep(.ivu-menu-item-active),
:deep(.ivu-menu-item-selected) {
  background: rgba(79, 70, 229, 0.1);
  color: var(--nexus-primary);
  border-bottom: none !important;
}

:deep(.ivu-menu-horizontal) {
  border-bottom: none !important;
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  height: auto;
  line-height: normal;
}

:deep(.ivu-menu-submenu) {
  float: none !important;
  display: inline-block;
}

// Dropdown menu styling
:deep(.ivu-select-dropdown),
:deep(.ivu-dropdown-menu) {
  border-radius: var(--nexus-radius-lg);
  border: 1px solid var(--nexus-border);
  background: var(--nexus-surface);
  box-shadow: var(--nexus-shadow-lg);
  margin-top: 8px;
  padding: 8px;
}

:deep(.ivu-dropdown-item) {
  font-size: 14px;
  padding: 8px 12px;
  border-radius: var(--nexus-radius);
  transition: var(--nexus-transition);
  color: var(--nexus-text-primary);

  &:hover {
    background: var(--nexus-surface-hover);
    color: var(--nexus-primary);
  }
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--nexus-text-primary);
}
</style>

<style lang="less">
/* Global overrides for NavBar */
#header .ivu-menu-horizontal,
#header .ivu-menu-horizontal:before,
#header .ivu-menu-horizontal:after {
  border-bottom: none !important;
  box-shadow: none !important;
  background: transparent !important;
}

#header .ivu-menu-light {
  background: transparent !important;
}
</style>
