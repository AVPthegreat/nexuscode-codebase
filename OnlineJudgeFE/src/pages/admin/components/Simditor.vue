<template>
  <textarea ref="editor"></textarea>
</template>

<script>
  import Simditor from 'tar-simditor'
  import 'tar-simditor/styles/simditor.css'
  import 'tar-simditor-markdown'
  import 'tar-simditor-markdown/styles/simditor-markdown.css'
  import './simditor-file-upload'

  // Override Simditor locale to English
  Simditor.locale = 'en-US'

  export default {
    name: 'Simditor',
    props: {
      toolbar: {
        type: Array,
        default: () => ['title', 'bold', 'italic', 'underline', 'fontScale', 'color', 'ol', 'ul', '|', 'blockquote', 'code', 'link', 'table', 'image', 'uploadfile', 'hr', '|', 'indent', 'outdent', 'alignment', '|', 'markdown']
      },
      value: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        editor: null,
        currentValue: this.value
      }
    },
    mounted () {
      // Force English locale
      Simditor.locale = 'en-US'
      
      this.editor = new Simditor({
        textarea: this.$refs.editor,
        toolbar: this.toolbar,
        pasteImage: true,
        markdown: false,
        locale: 'en-US',
        tabIndent: false,
        upload: {
          url: '/api/admin/upload_image/',
          params: null,
          fileKey: 'image',
          connectionCount: 3,
          leaveConfirm: this.$i18n.t('m.Uploading_is_in_progress')
        },
        allowedStyles: {
          span: ['color']
        }
      })
      
      // Override any remaining Chinese text after initialization
      setTimeout(() => {
        const dropdowns = this.$el.querySelectorAll('.simditor-toolbar .toolbar-item-title .toolbar-item-list')
        dropdowns.forEach(dropdown => {
          const items = dropdown.querySelectorAll('li')
          items.forEach(item => {
            const text = item.textContent.trim()
            // Replace Chinese text with English equivalents
            if (text === '普通文本' || text === '一般文字') item.textContent = 'Normal'
            if (text === '标题 1' || text === '標題 1') item.textContent = 'Heading 1'
            if (text === '标题 2' || text === '標題 2') item.textContent = 'Heading 2'
            if (text === '标题 3' || text === '標題 3') item.textContent = 'Heading 3'
            if (text === '标题 4' || text === '標題 4') item.textContent = 'Heading 4'
            if (text === '标题 5' || text === '標題 5') item.textContent = 'Heading 5'
          })
        })
      }, 100)
      
      this.editor.on('valuechanged', (e, src) => {
        this.currentValue = this.editor.getValue()
      })
      this.editor.on('decorate', (e, src) => {
        this.currentValue = this.editor.getValue()
      })

      this.editor.setValue(this.value)
    },
    watch: {
      'value' (val) {
        if (this.currentValue !== val) {
          this.currentValue = val
          this.editor.setValue(val)
        }
      },
      'currentValue' (newVal, oldVal) {
        if (newVal !== oldVal) {
          this.$emit('change', newVal)
          this.$emit('input', newVal)
        }
      }
    }
  }
</script>

<style lang="less" scoped>
</style>
