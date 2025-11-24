<template>
  <div class="split-container">
    <!-- Left Column: Problem Description & Info -->
    <div id="problem-left">
      <Card :padding="20" dis-hover class="full-height-card">
        <Tabs value="description" :animated="false">
          <TabPane :label="$t('m.Description')" name="description">
            <div id="problem-content" class="markdown-body" v-katex>
              <div class="header-title">{{ problem.title }}</div>
              <p class="title">{{ $t('m.Description') }}</p>
              <p class="content" v-html=problem.description></p>

              <p class="title">{{ $t('m.Input') }} <span v-if="problem.io_mode.io_mode == 'File IO'">({{
                $t('m.FromFile') }}:
                  {{ problem.io_mode.input }})</span></p>
              <p class="content" v-html=problem.input_description></p>

              <p class="title">{{ $t('m.Output') }} <span v-if="problem.io_mode.io_mode == 'File IO'">({{ $t('m.ToFile')
                  }}:
                  {{ problem.io_mode.output }})</span></p>
              <p class="content" v-html=problem.output_description></p>

              <div v-for="(sample, index) of problem.samples" :key="index">
                <div class="flex-container sample">
                  <div class="sample-input">
                    <p class="title">{{ $t('m.Sample_Input') }} {{ index + 1 }}
                      <a class="copy" v-clipboard:copy="sample.input" v-clipboard:success="onCopy"
                        v-clipboard:error="onCopyError">
                        <Icon type="clipboard"></Icon>
                      </a>
                    </p>
                    <pre>{{ sample.input }}</pre>
                  </div>
                  <div class="sample-output">
                    <p class="title">{{ $t('m.Sample_Output') }} {{ index + 1 }}</p>
                    <pre>{{ sample.output }}</pre>
                  </div>
                </div>
              </div>

              <div v-if="problem.hint">
                <p class="title">{{ $t('m.Hint') }}</p>
                <Card dis-hover>
                  <div class="content" v-html=problem.hint></div>
                </Card>
              </div>

              <div v-if="problem.source">
                <p class="title">{{ $t('m.Source') }}</p>
                <p class="content">{{ problem.source }}</p>
              </div>

              <div class="editorial-section">
                <p class="title">Editorial</p>
                <div v-if="editorialLoading">
                  <Spin size="large"></Spin>
                </div>
                <div v-else-if="editorialError">
                  <Alert type="warning" show-icon>{{ editorialError }}</Alert>
                </div>
                <div v-else-if="editorial">
                  <Card dis-hover>
                    <div class="content" v-html="editorial"></div>
                  </Card>
                </div>
                <div v-else>
                  <Button type="primary" @click="loadEditorial" :loading="editorialLoading">
                    View Editorial
                  </Button>
                </div>
              </div>
            </div>
          </TabPane>

          <TabPane :label="$t('m.Information')" name="info">
            <div class="info-content">
              <ul>
                <li>
                  <p>ID</p>
                  <p>{{ problem._id }}</p>
                </li>
                <li>
                  <p>{{ $t('m.Time_Limit') }}</p>
                  <p>{{ problem.time_limit }}MS</p>
                </li>
                <li>
                  <p>{{ $t('m.Memory_Limit') }}</p>
                  <p>{{ problem.memory_limit }}MB</p>
                </li>
                <li>
                  <p>{{ $t('m.IOMode') }}</p>
                  <p>{{ problem.io_mode.io_mode }}</p>
                </li>
                <li>
                  <p>{{ $t('m.Created') }}</p>
                  <p>{{ problem.created_by.username }}</p>
                </li>
                <li v-if="problem.difficulty">
                  <p>{{ $t('m.Level') }}</p>
                  <p>{{ $t('m.' + problem.difficulty) }}</p>
                </li>
                <li v-if="problem.total_score">
                  <p>{{ $t('m.Score') }}</p>
                  <p>{{ problem.total_score }}</p>
                </li>
                <li>
                  <p>{{ $t('m.Tags') }}</p>
                  <p>
                    <Tag v-for="tag in problem.tags" :key="tag">{{ tag }}</Tag>
                  </p>
                </li>
              </ul>
            </div>
          </TabPane>

          <TabPane :label="$t('m.Statistic')" name="statistics">
            <div class="echarts">
              <ECharts :options="pie"></ECharts>
            </div>
          </TabPane>
        </Tabs>
      </Card>
    </div>

    <!-- Right Column: Code Editor -->
    <div id="problem-right">
      <Card :padding="0" dis-hover class="full-height-card editor-card">
        <div class="editor-header">
          <span class="lang-select">
            <span>Language: </span>
            <Select :value="language" @on-change="onChangeLang" size="small" style="width: 100px">
              <Option v-for="item in problem.languages" :value="item" :key="item">{{ item }}</Option>
            </Select>
          </span>
          <span class="theme-select">
            <span>Theme: </span>
            <Select :value="theme" @on-change="onChangeTheme" size="small" style="width: 100px">
              <Option value="solarized">Solarized</Option>
              <Option value="monokai">Monokai</Option>
              <Option value="material">Material</Option>
            </Select>
          </span>
          <Button type="text" icon="refresh" @click="onResetToTemplate">{{ $t('m.Reset_to_default_code_definition')
            }}</Button>
        </div>

        <div class="editor-container">
          <CodeMirror :value.sync="code" :languages="problem.languages" :language="language" :theme="theme"
            @resetCode="onResetToTemplate" @changeTheme="onChangeTheme" @changeLang="onChangeLang"></CodeMirror>
        </div>

        <div class="editor-footer">
          <Row type="flex" justify="space-between" align="middle">
            <Col :span="12">
            <div class="status" v-if="statusVisible">
              <template v-if="!this.contestID || (this.contestID && OIContestRealTimePermission)">
                <Tag type="dot" :color="submissionStatus.color" @click.native="handleRoute('/status/' + submissionId)">
                  {{ $t('m.' + submissionStatus.text.replace(/ /g, "_")) }}
                </Tag>
              </template>
              <template v-else-if="this.contestID && !OIContestRealTimePermission">
                <Alert type="success" show-icon>{{ $t('m.Submitted_successfully') }}</Alert>
              </template>
            </div>
            <div v-else-if="problem.my_status === 0">
              <Alert type="success" show-icon>{{ $t('m.You_have_solved_the_problem') }}</Alert>
            </div>
            </Col>
            <Col :span="12" style="text-align: right;">
            <template v-if="captchaRequired">
              <div class="captcha-container">
                <Tooltip v-if="captchaRequired" content="Click to refresh" placement="top">
                  <img :src="captchaSrc" @click="getCaptchaSrc" />
                </Tooltip>
                <Input v-model="captchaCode" class="captcha-code" />
              </div>
            </template>
            <Button type="warning" icon="edit" :loading="submitting" @click="submitCode"
              :disabled="problemSubmitDisabled || submitted">
              <span v-if="submitting">{{ $t('m.Submitting') }}</span>
              <span v-else>{{ $t('m.Submit') }}</span>
            </Button>
            <Button type="primary" icon="help-buoy" :loading="hintLoading" @click="getAIHint"
              style="margin-left: 10px;">
              <span v-if="hintLoading">Thinking...</span>
              <span v-else>AI Hint</span>
            </Button>
            </Col>
          </Row>
        </div>
      </Card>
    </div>

    <!-- AI Hint Modal -->
    <Modal v-model="hintVisible" title="AI Senpai Says..." width="600">
      <div class="markdown-body" v-html="hintContent"></div>
      <div slot="footer">
        <Button type="primary" @click="hintVisible = false">Got it!</Button>
      </div>
    </Modal>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import { types } from '../../../../store'
import CodeMirror from '@oj/components/CodeMirror.vue'
import storage from '@/utils/storage'
import { FormMixin } from '@oj/components/mixins'
import { JUDGE_STATUS, CONTEST_STATUS, buildProblemCodeKey } from '@/utils/constants'
import api from '@oj/api'
import { pie, largePie } from './chartData'

// 只显示这些状态的图形占用
const filtedStatus = ['-1', '-2', '0', '1', '2', '3', '4', '8']

export default {
  name: 'Problem',
  components: {
    CodeMirror
  },
  mixins: [FormMixin],
  data() {
    return {
      statusVisible: false,
      captchaRequired: false,
      graphVisible: false,
      submissionExists: false,
      captchaCode: '',
      captchaSrc: '',
      contestID: '',
      problemID: '',
      submitting: false,
      code: '',
      language: 'C++',
      theme: 'solarized',
      submissionId: '',
      submitted: false,
      result: {
        result: 9
      },
      problem: {
        title: '',
        description: '',
        hint: '',
        my_status: '',
        template: {},
        languages: [],
        created_by: {
          username: ''
        },
        tags: [],
        io_mode: { 'io_mode': 'Standard IO' }
      },
      pie: pie,
      largePie: largePie,
      // echarts 无法获取隐藏dom的大小，需手动指定
      largePieInitOpts: {
        width: '500',
        height: '480'
      },
      editorial: null,
      editorialLoading: false,
      editorialError: null,
      activePanel: 'info', // default panel
      discussionMessage: '',
      hintLoading: false,
      hintVisible: false,
      hintContent: ''
    }
  },
  beforeRouteEnter(to, from, next) {
    let problemCode = storage.get(buildProblemCodeKey(to.params.problemID, to.params.contestID))
    if (problemCode) {
      next(vm => {
        vm.language = problemCode.language
        vm.code = problemCode.code
        vm.theme = problemCode.theme
      })
    } else {
      next()
    }
  },
  mounted() {
    this.$store.commit(types.CHANGE_CONTEST_ITEM_VISIBLE, { menu: false })
    // Ensure scrolling works in fullscreen during contest
    if (this.$store.state.contest && this.$store.state.contest.started) {
      document.documentElement.style.overflow = 'auto'
      document.body.style.overflow = 'auto'
    }

    // Set default editor theme based on global theme
    this.updateThemeFromGlobal()

    // Listen for theme changes
    this.themeObserver = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'class') {
          this.updateThemeFromGlobal()
        }
      })
    })
    this.themeObserver.observe(document.body, { attributes: true })

    this.init()
  },
  beforeDestroy() {
    if (this.themeObserver) {
      this.themeObserver.disconnect()
    }
  },
  methods: {
    ...mapActions(['changeDomTitle']),
    updateThemeFromGlobal() {
      if (document.body.classList.contains('dark-mode')) {
        this.theme = 'material'
      } else {
        this.theme = 'solarized'
      }
    },
    handleViewOverview() {
      this.$router.push({ name: 'contest-details', params: { contestID: this.contestID } })
    },
    handleSubmitContest() {
      this.$Modal.confirm({
        title: 'Submit Contest',
        content: 'Are you sure you want to finish and submit the contest? You will be redirected to the overview page.',
        onOk: () => {
          // Submit all localStorage data to backend
          this.$store.dispatch('submitContestFromLocal', this.contestID).then(() => {
            this.$store.commit(types.CONTEST_RESET_LOCK, { contestID: this.contestID })
            document.documentElement.style.overflow = ''
            document.body.style.overflow = ''
            this.$Message.success('Contest submitted successfully')
            this.$router.push({ name: 'contest-details', params: { contestID: this.contestID } })
          }).catch(() => {
            this.$Message.error('Failed to submit contest')
          })
        }
      })
    },
    sendDiscussion() {
      const msg = this.discussionMessage.trim()
      if (!msg) { return }
      if (!this.$store.getters.isAuthenticated) {
        this.$Message.warning('Please login to post a discussion message')
        this.$store.dispatch('changeModalStatus', { mode: 'login', visible: true })
        return
      }
      const payload = { problem_id: this.problemID, message: msg }
      api.createDiscussion(payload).then(() => {
        this.$Message.success('Message sent')
        this.discussionMessage = ''
      }).catch((err) => {
        const msg = (err && err.data && err.data.data) || 'Failed to send message'
        this.$Message.error(msg)
      })
    },
    goToSubmissions() {
      this.$router.push(this.submissionRoute)
    },
    init() {
      this.$Loading.start()
      this.contestID = this.$route.params.contestID
      this.problemID = this.$route.params.problemID
      let func = this.$route.name === 'problem-details' ? 'getProblem' : 'getContestProblem'
      api[func](this.problemID, this.contestID).then(res => {
        this.$Loading.finish()
        let problem = res.data.data
        this.changeDomTitle({ title: problem.title })
        api.submissionExists(problem.id).then(res => {
          this.submissionExists = res.data.data
        })
        problem.languages = problem.languages.sort()
        this.problem = problem
        if (problem.statistic_info) {
          this.changePie(problem)
        }

        // 在beforeRouteEnter中修改了, 说明本地有code，无需加载template
        if (this.code !== '') {
          return
        }
        // try to load problem template
        this.language = this.problem.languages[0]
        let template = this.problem.template
        if (template && template[this.language]) {
          this.code = template[this.language]
        }
      }, () => {
        this.$Loading.error()
      })
    },
    changePie(problemData) {
      // 只显示特定的一些状态
      for (let k in problemData.statistic_info) {
        if (filtedStatus.indexOf(k) === -1) {
          delete problemData.statistic_info[k]
        }
      }
      let acNum = problemData.accepted_number
      let data = [
        { name: 'WA', value: problemData.submission_number - acNum },
        { name: 'AC', value: acNum }
      ]
      this.pie.series[0].data = data
      // 只把大图的AC selected下，这里需要做一下deepcopy
      let data2 = JSON.parse(JSON.stringify(data))
      data2[1].selected = true
      this.largePie.series[1].data = data2

      // 根据结果设置legend,没有提交过的legend不显示
      let legend = Object.keys(problemData.statistic_info).map(ele => JUDGE_STATUS[ele].short)
      if (legend.length === 0) {
        legend.push('AC', 'WA')
      }
      this.largePie.legend.data = legend

      // 把ac的数据提取出来放在最后
      let acCount = problemData.statistic_info['0']
      delete problemData.statistic_info['0']

      let largePieData = []
      Object.keys(problemData.statistic_info).forEach(ele => {
        largePieData.push({ name: JUDGE_STATUS[ele].short, value: problemData.statistic_info[ele] })
      })
      largePieData.push({ name: 'AC', value: acCount })
      this.largePie.series[0].data = largePieData
    },
    handleRoute(route) {
      this.$router.push(route)
    },
    onChangeLang(newLang) {
      if (this.problem.template[newLang]) {
        if (this.code.trim() === '') {
          this.code = this.problem.template[newLang]
        }
      }
      this.language = newLang
    },
    onChangeTheme(newTheme) {
      this.theme = newTheme
    },
    onResetToTemplate() {
      this.$Modal.confirm({
        content: this.$i18n.t('m.Are_you_sure_you_want_to_reset_your_code'),
        onOk: () => {
          let template = this.problem.template
          if (template && template[this.language]) {
            this.code = template[this.language]
          } else {
            this.code = ''
          }
        }
      })
    },
    checkSubmissionStatus() {
      // 使用setTimeout避免一些问题
      if (this.refreshStatus) {
        // 如果之前的提交状态检查还没有停止,则停止,否则将会失去timeout的引用造成无限请求
        clearTimeout(this.refreshStatus)
      }
      const checkStatus = () => {
        let id = this.submissionId
        api.getSubmission(id).then(res => {
          this.result = res.data.data
          if (Object.keys(res.data.data.statistic_info).length !== 0) {
            this.submitting = false
            this.submitted = false
            clearTimeout(this.refreshStatus)

            // Update problem stats in localStorage if in contest
            if (this.contestID && this.$store.state.contest.started) {
              const submissionResult = res.data.data
              const info = submissionResult.info || {}
              const testcases = info.data || []
              const passedCases = testcases.filter(tc => tc.result === 0).length
              const totalCases = testcases.length

              this.$store.dispatch('updateProblemStatsLocal', {
                contestID: this.contestID,
                problemID: this.problemID,
                stats: {
                  attempts: 1, // will be incremented in store
                  result: submissionResult.result,
                  passed_cases: passedCases,
                  total_cases: totalCases,
                  score: totalCases > 0 ? Math.floor((passedCases / totalCases) * 100) : 0
                }
              })
            }

            this.init()
          } else {
            this.refreshStatus = setTimeout(checkStatus, 2000)
          }
        }, res => {
          this.submitting = false
          clearTimeout(this.refreshStatus)
        })
      }
      this.refreshStatus = setTimeout(checkStatus, 2000)
    },
    submitCode() {
      if (this.code.trim() === '') {
        this.$error(this.$i18n.t('m.Code_can_not_be_empty'))
        return
      }
      this.submissionId = ''
      this.result = { result: 9 }
      this.submitting = true
      let data = {
        problem_id: this.problem.id,
        language: this.language,
        code: this.code,
        contest_id: this.contestID
      }
      if (this.captchaRequired) {
        data.captcha = this.captchaCode
      }
      const submitFunc = (data, detailsVisible) => {
        this.statusVisible = true
        api.submitCode(data).then(res => {
          this.submissionId = res.data.data && res.data.data.submission_id

          // Save submission to localStorage if in contest
          if (this.contestID && this.$store.state.contest.started) {
            this.$store.dispatch('saveSubmissionLocal', {
              contestID: this.contestID,
              submissionData: {
                submission_id: this.submissionId,
                problem_id: this.problem.id,
                problem_title: this.problem.title,
                language: this.language,
                code: this.code,
                result: 9 // pending initially
              }
            })
          }

          // 定时检查状态
          this.submitting = false
          this.submissionExists = true
          if (!detailsVisible) {
            this.$Modal.success({
              title: this.$i18n.t('m.Success'),
              content: this.$i18n.t('m.Submit_code_successfully')
            })
            return
          }
          this.submitted = true
          this.checkSubmissionStatus()
        }, res => {
          this.getCaptchaSrc()
          if (res.data.data.startsWith('Captcha is required')) {
            this.captchaRequired = true
          }
          this.submitting = false
          this.statusVisible = false
        })
      }

      if (this.contestRuleType === 'OI' && !this.OIContestRealTimePermission) {
        if (this.submissionExists) {
          this.$Modal.confirm({
            title: '',
            content: '<h3>' + this.$i18n.t('m.You_have_submission_in_this_problem_sure_to_cover_it') + '<h3>',
            onOk: () => {
              // 暂时解决对话框与后面提示对话框冲突的问题(否则一闪而过）
              setTimeout(() => {
                submitFunc(data, false)
              }, 1000)
            },
            onCancel: () => {
              this.submitting = false
            }
          })
        } else {
          submitFunc(data, false)
        }
      } else {
        submitFunc(data, true)
      }
    },
    onCopy(event) {
      this.$success('Code copied')
    },
    onCopyError(e) {
      this.$error('Failed to copy code')
    },
    loadEditorial() {
      this.editorialLoading = true
      this.editorialError = null
      api.getProblemEditorial(this.problem.id).then(res => {
        this.editorial = res.data.data.editorial
        this.editorialLoading = false
      }).catch(err => {
        this.editorialLoading = false
        if (err.response && err.response.status === 403) {
          this.editorialError = 'You need to solve this problem first to view the editorial, or wait for the contest to end.'
        } else if (err.response && err.response.data && err.response.data.error) {
          this.editorialError = err.response.data.error
        } else {
          this.editorialError = 'Failed to load editorial. Please try again later.'
        }
      })
    },
    getAIHint() {
      if (this.code.trim() === '') {
        this.$error('Please write some code first so I can help you!')
        return
      }
      this.hintLoading = true
      let data = {
        problem_id: this.problem._id,
        code: this.code,
        language: this.language,
        question: this.discussionMessage // optional: use discussion input as context
      }
      api.getProblemHint(data).then(res => {
        this.hintLoading = false
        // Simple markdown to html conversion (basic) or just display text
        // Since we have v-katex and markdown-body, we can try to render it.
        // For now, let's just wrap in p tags if it's plain text, or rely on existing markdown renderers if available.
        // Actually, let's just use a simple replace for newlines to br for now if not using a full renderer
        this.hintContent = res.data.data.replace(/\n/g, '<br>')
        this.hintVisible = true
      }, _ => {
        this.hintLoading = false
      })
    }
  },
  computed: {
    ...mapGetters(['problemSubmitDisabled', 'contestRuleType', 'OIContestRealTimePermission', 'contestStatus']),
    contestStarted() { return this.$store.state.contest.started },
    contest() {
      return this.$store.state.contest.contest
    },
    contestEnded() {
      return this.contestStatus === CONTEST_STATUS.ENDED
    },
    submissionStatus() {
      return {
        text: JUDGE_STATUS[this.result.result]['name'],
        color: JUDGE_STATUS[this.result.result]['color']
      }
    },
    submissionRoute() {
      // Always pass the selected problemID for submissions
      if (this.contestID) {
        return { name: 'contest-submission-list', query: { problemID: this.problemID } }
      } else {
        return { name: 'submission-list', query: { problemID: this.problemID } }
      }
    }
  },
  beforeRouteLeave(to, from, next) {
    // 防止切换组件后仍然不断请求
    clearInterval(this.refreshStatus)

    this.$store.commit(types.CHANGE_CONTEST_ITEM_VISIBLE, { menu: true })
    storage.set(buildProblemCodeKey(this.problem._id, from.params.contestID), {
      code: this.code,
      language: this.language,
      theme: this.theme
    })
    next()
  },
  watch: {
    '$route'() {
      this.init()
    }
  }
}
</script>

<style lang="less" scoped>
.split-container {
  background-color: red;
  display: flex;
  flex-direction: row;
  height: calc(100vh - 80px);
  /* Occupy full height minus navbar */
  width: 100%;
  overflow: hidden;
  padding: 10px;
  gap: 10px;
}

#problem-left {
  flex: 0 0 40%;
  /* 40% width */
  height: 100%;
  overflow-y: auto;
  min-width: 350px;
}

#problem-right {
  flex: 1;
  /* Remaining space */
  height: 100%;
  display: flex;
  flex-direction: column;
}

.full-height-card {
  height: 100%;
  display: flex;
  flex-direction: column;

  /deep/ .ivu-card-body {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }
}

.editor-card {
  /deep/ .ivu-card-body {
    padding: 0;
    display: flex;
    flex-direction: column;
  }
}

.editor-header {
  padding: 10px 15px;
  border-bottom: 1px solid #eee;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: space-between;

  .lang-select,
  .theme-select {
    margin-right: 15px;

    span {
      margin-right: 5px;
      font-weight: bold;
    }
  }
}

.editor-container {
  flex: 1;
  overflow: hidden;
  position: relative;

  /* Force CodeMirror to take full height */
  /deep/ .CodeMirror {
    height: 100% !important;
  }
}

.editor-footer {
  padding: 10px 15px;
  border-top: 1px solid #eee;
  background: #fff;
}

.header-title {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #333;
}

#problem-content {
  .title {
    font-size: 16px;
    font-weight: 600;
    margin: 20px 0 10px 0;
    color: #409EFF;
  }

  .content {
    // background-color: red;
    font-size: 14px;
    line-height: 1.6;
  }
}

.sample {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  align-items: stretch;

  &-input,
  &-output {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  pre {
    flex: 1;
    padding: 10px;
    background: #f7f7f7;
    border-radius: 4px;
    font-family: monospace;
    white-space: pre-wrap;
  }
}

.info-content {
  ul {
    list-style: none;
    padding: 0;

    li {
      display: flex;
      justify-content: space-between;
      padding: 10px 0;
      border-bottom: 1px dashed #eee;

      &:last-child {
        border-bottom: none;
      }

      p:first-child {
        font-weight: bold;
        color: #666;
      }
    }
  }
}

/* Dark mode overrides */
:global(.dark-mode) {

  .editor-header,
  .editor-footer {
    background: #2d2d2d;
    border-color: #444;
  }

  .header-title {
    color: #eee;
  }

  .sample pre {
    background: #333;
    color: #eee;
  }

  .info-content li {
    border-bottom-color: #444;

    p:first-child {
      color: #aaa;
    }
  }
}
</style>
