<template>
  <div class="dashboard-container">
    <!-- Secondary Navbar -->
    <div class="secondary-navbar">
      <div class="nav-content">
        <div :class="['nav-item', { active: isRoute('user-home') }]" @click="goRoute('/user-home')">
          <Icon type="ios-book-outline"></Icon> Overview
        </div>
        <div :class="['nav-item', { active: isRoute('profile-setting') || isRoute('default-setting') }]"
          @click="goRoute('/setting/profile')">
          <Icon type="ios-person-outline"></Icon> Profile
        </div>
        <div :class="['nav-item', { active: isRoute('account-setting') }]" @click="goRoute('/setting/account')">
          <Icon type="ios-gear-outline"></Icon> Account
        </div>
        <div :class="['nav-item', { active: isRoute('security-setting') }]" @click="goRoute('/setting/security')">
          <Icon type="ios-locked-outline"></Icon> Security
        </div>
        <div class="nav-item" v-if="isAdminRole" @click="goToAdmin">
          <Icon type="ios-settings-strong"></Icon> Admin Panel
        </div>
        <div class="nav-item logout" @click="handleLogout">
          <Icon type="log-out"></Icon> Logout
        </div>
      </div>
    </div>

    <div class="dashboard-grid">
      <!-- Left Column: Profile Sidebar -->
      <div class="col-left">
        <div class="profile-sidebar">
          <div class="avatar-section">
            <img class="avatar" :src="profile.avatar" />
            <div class="status-badge" v-if="profile.mood">
              <Icon type="happy-outline"></Icon>
            </div>
          </div>

          <div class="profile-names">
            <h1 class="fullname">{{ profile.user ? profile.user.username : '' }}</h1>
            <h2 class="username">{{ profile.user ? profile.user.username : '' }}</h2>
          </div>

          <div class="profile-bio" v-if="profile.mood">
            {{ profile.mood }}
          </div>

          <div class="profile-meta">
            <div class="meta-item" v-if="profile.school">
              <Icon type="ios-people-outline" class="meta-icon"></Icon>
              <span>{{ profile.school }}</span>
            </div>
            <div class="meta-item">
              <Icon type="ios-location-outline" class="meta-icon"></Icon>
              <span>India</span>
            </div>
            <div class="meta-item" v-if="profile.user && profile.user.email">
              <Icon type="ios-email-outline" class="meta-icon"></Icon>
              <a :href="'mailto:' + profile.user.email">{{ profile.user.email }}</a>
            </div>
            <div class="meta-item" v-if="profile.blog">
              <Icon type="link" class="meta-icon"></Icon>
              <a :href="profile.blog" target="_blank">{{ profile.blog }}</a>
            </div>
            <div class="meta-item" v-if="profile.github">
              <Icon type="social-github" class="meta-icon"></Icon>
              <a :href="profile.github" target="_blank">{{ getGithubUsername(profile.github) }}</a>
            </div>
          </div>

          <div class="gamification-stats">
            <div class="level-info">
              <span class="level-label">Level {{ level }}</span>
              <Progress :percent="xpPercent" status="active" :stroke-width="6" hide-info class="xp-progress"></Progress>
              <span class="xp-text">{{ profile.xp }} / {{ nextLevelXp }} XP</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Settings Content -->
      <div class="col-content">
        <transition name="fadeInUp" mode="out-in">
          <router-view></router-view>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import api from '@oj/api'

export default {
  name: 'Settings',
  data() {
    return {
      username: ''
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    ...mapActions(['changeDomTitle']),
    init() {
      this.username = this.$store.getters.user.username
      this.changeDomTitle({ title: 'Settings' })
    },
    goRoute(route) {
      this.$router.push(route)
    },
    isRoute(name) {
      return this.$route.name === name
    },
    handleLogout() {

      api.logout().then(() => {
        this.$success('Logged out successfully')
        this.$router.push('/')
        location.reload()
      })
    },
    getGithubUsername(url) {
      if (!url) return ''
      const cleanUrl = url.endsWith('/') ? url.slice(0, -1) : url
      return cleanUrl.split('/').pop()
    },
    goToAdmin() {
      window.open('/admin/')
    }
  },
  computed: {
    ...mapGetters(['user', 'profile', 'isAdminRole']),
    level() {
      if (!this.profile.xp) return 1
      return Math.floor(Math.sqrt(this.profile.xp / 10)) + 1
    },
    nextLevelXp() {
      return 10 * Math.pow(this.level, 2)
    },
    xpPercent() {
      if (!this.profile.xp) return 0
      let currentLevelStart = 10 * Math.pow(this.level - 1, 2)
      let nextLevelStart = 10 * Math.pow(this.level, 2)
      let progress = (this.profile.xp - currentLevelStart) / (nextLevelStart - currentLevelStart) * 100
      return Math.min(Math.max(progress, 0), 100)
    }
  }
}
</script>

<style lang="less" scoped>
.dashboard-container {
  width: 100%;
  margin-top: -37px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
}

// Secondary Navbar
.secondary-navbar {
  // border-top: 1px solid #d0d7de;
  background: #F3F4F6;
  margin-bottom: 32px;
  margin-top: 10px;
  border: none !important;
  position: sticky;
  top: 66px;
  z-index: 100;
  width: 100%;
  left: 0;
  right: 0;

  .nav-content {
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 32px;
    display: flex;
    gap: 8px;

    .nav-item {
      text-transform: uppercase;
      padding: 16px 28px;
      font-size: 14px;
      color: #24292f;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      border-bottom: 2px solid transparent;
      transition: all 0.2s;

      &:hover {
        background: rgba(208, 215, 222, 0.32);
        border-radius: 20px;
      }

      &.active {
        font-weight: 600;
        border-bottom-color: #fd8c73;

        i {
          color: #57606a;
        }
      }

      &.logout {
        margin-left: auto;
        color: #cf222e;

        &:hover {
          background: #ffebe9;
        }
      }
    }
  }
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 32px;
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 32px;
}

// Left Column: Profile Sidebar
.col-left {
  .profile-sidebar {
    position: sticky;
    top: 80px;

    .avatar-section {
      position: relative;
      margin-bottom: 16px;

      .avatar {
        width: 296px;
        height: 296px;
        border-radius: 50%;
        border: 1px solid #d0d7de;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        z-index: 1;
      }

      .status-badge {
        position: absolute;
        bottom: 30px;
        right: 30px;
        width: 38px;
        height: 38px;
        background: #fff;
        border: 1px solid #d0d7de;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        cursor: pointer;
        z-index: 2;

        &:hover {
          color: #0969da;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
      }
    }

    .profile-names {
      margin-bottom: 16px;

      .fullname {
        font-size: 24px;
        line-height: 1.25;
        font-weight: 600;
        color: #24292f;
      }

      .username {
        font-size: 20px;
        font-weight: 300;
        line-height: 24px;
        color: #57606a;
      }
    }

    .profile-bio {
      font-size: 16px;
      color: #24292f;
      margin-bottom: 16px;
    }

    .profile-meta {
      margin-bottom: 24px;

      .meta-item {
        display: flex;
        align-items: center;
        margin-top: 4px;
        font-size: 14px;
        color: #24292f;

        .meta-icon {
          width: 16px;
          margin-right: 8px;
          color: #57606a;
          text-align: center;
        }

        a {
          color: #24292f;

          &:hover {
            color: #0969da;
            text-decoration: underline;
          }
        }
      }
    }

    .gamification-stats {
      padding-top: 16px;
      border-top: 1px solid #d0d7de;

      .level-info {
        .level-label {
          display: block;
          font-weight: 600;
          margin-bottom: 4px;
          color: #24292f;
        }

        .xp-text {
          display: block;
          font-size: 12px;
          color: #57606a;
          margin-top: 4px;
        }
      }
    }
  }
}

// Center Column: Main Content
.col-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-bottom: 48px;
}

// Dark Mode Support
.dark-mode {
  .secondary-navbar {
    background: #0C1222;
    border-top-color: #30363d;

    .nav-item {
      color: #fff;

      &:hover {
        background: rgba(177, 186, 196, 0.12);
      }

      &.active {
        border-bottom-color: #f78166;

        i {
          color: #8b949e;
        }
      }
    }
  }

  .col-left {
    .profile-sidebar {
      .avatar-section {
        .avatar {
          border-color: #30363d;
        }

        .status-badge {
          background: #0d1117;
          border-color: #30363d;
          color: #c9d1d9;
        }
      }

      .profile-names {
        .fullname {
          color: #c9d1d9;
        }

        .username {
          color: #ffffff;
        }
      }

      .profile-bio {
        color: #c9d1d9;
      }

      .profile-meta .meta-item {
        color: #c9d1d9;

        .meta-icon {
          color: #8b949e;
        }

        a {
          color: #c9d1d9;
        }
      }

      .gamification-stats .level-info {
        .level-label {
          color: #c9d1d9;
        }

        .xp-text {
          color: #8b949e;
        }
      }
    }
  }
}

// Media Queries
@media (max-width: 900px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
    padding: 0 16px;
  }

  .col-left .profile-sidebar {
    position: static;
    margin-bottom: 32px;

    .avatar-section .avatar {
      width: 100px;
      height: 100px;
    }
  }

  .secondary-navbar .nav-content {
    padding: 0 16px;
    overflow-x: auto;
  }
}
</style>
