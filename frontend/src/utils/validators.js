// Mock validators for academic data

export const validateORCID = async (orcid) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Basic format check: 0000-0000-0000-0000 or 0000-0000-0000-000X
      const regex = /^\d{4}-\d{4}-\d{4}-[\dXx]{4}$/
      if (!regex.test(orcid)) {
        resolve({ valid: false, message: 'Invalid format. Use 0000-0000-0000-0000.' })
        return
      }
      
      // Mock API check: Randomly fail some
      if (orcid.endsWith('0000')) {
        resolve({ valid: false, message: 'ORCID not found in registry.' })
      } else {
        resolve({ valid: true, message: 'Verified via ORCID.org' })
      }
    }, 800)
  })
}

export const validateDOI = async (doi) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Basic DOI format: 10.xxxx/xxxxx
      const regex = /^10\.\d{4,9}\/[-._;()/:a-zA-Z0-9]+$/
      if (!regex.test(doi)) {
        resolve({ valid: false, message: 'Invalid DOI format. Start with 10.' })
        return
      }
      
      resolve({ valid: true, message: 'DOI resolved successfully.' })
    }, 800)
  })
}

export const searchInstitutions = async (query) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      if (!query || query.length < 2) {
        resolve([])
        return
      }
      
      const mockDB = [
        'Harvard University',
        'Stanford University',
        'Massachusetts Institute of Technology (MIT)',
        'University of Oxford',
        'University of Cambridge',
        'Tsinghua University',
        'Peking University',
        'Fudan University',
        'Shanghai Jiao Tong University',
        'University of Tokyo',
        'National University of Singapore',
        'ETH Zurich',
        'University of Toronto',
        'Johns Hopkins University',
        'University of California, Berkeley'
      ]
      
      const results = mockDB.filter(i => i.toLowerCase().includes(query.toLowerCase()))
      resolve(results)
    }, 500)
  })
}
