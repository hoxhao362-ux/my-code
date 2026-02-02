export const useErrorScroll = () => {
  const scrollToError = () => {
    // Wait for DOM update
    setTimeout(() => {
      // Find first error element
      // Selectors: .error, .required (if empty), .error-text, .error-border, .error-msg
      // We prioritize specific error messages or fields marked as error
      
      const errorSelectors = [
        '.error-text',
        '.error-msg',
        '.error-border',
        '.char-count.error',
        'input:invalid',
        'select:invalid',
        'textarea:invalid'
      ]
      
      let firstError = null
      for (const selector of errorSelectors) {
        const el = document.querySelector(selector)
        if (el) {
          firstError = el
          break
        }
      }
      
      // If no explicit error class found, check for required empty fields if the step status is error?
      // But usually the validation logic in store sets the step status. 
      // The components render error messages based on store state.
      
      if (firstError) {
        // Scroll to the element with some padding
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' })
        // Optional: focus if it's an input
        const input = firstError.closest('.form-group')?.querySelector('input, select, textarea')
        if (input) input.focus()
      }
    }, 100)
  }
  
  return { scrollToError }
}
