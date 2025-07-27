import JSZip from 'jszip'

export function useZipCreation() {
  const createZip = async (files) => {
    try {
      const zip = new JSZip()

      // Add the single markdown file (validated to be exactly one)
      const markdownFiles = files.filter(f => f.type === 'markdown')
      if (markdownFiles.length === 1) {
        const markdownFile = markdownFiles[0]
        zip.file(markdownFile.file.name, markdownFile.file)
      }
      else {
        throw new Error('Exactly one markdown file is required')
      }

      // Add images to images/ folder
      const imageFiles = files.filter(f => f.type === 'image')
      for (const fileObj of imageFiles) {
        zip.file(`images/${fileObj.file.name}`, fileObj.file)
      }

      // Generate the ZIP file
      const zipBlob = await zip.generateAsync({
        type: 'blob',
        compression: 'DEFLATE',
        compressionOptions: {
          level: 6,
        },
      })

      return zipBlob
    }
    catch (error) {
      console.error('Failed to create ZIP file:', error)
      throw new Error(`ZIP creation failed: ${error.message}`)
    }
  }

  const validateZipStructure = (files) => {
    const markdownFiles = files.filter(f => f.type === 'markdown')
    const imageFiles = files.filter(f => f.type === 'image')

    const errors = []

    if (markdownFiles.length !== 1) {
      errors.push('Exactly one markdown file is required for ZIP creation')
    }

    // Check for duplicate filenames in images
    const imageNames = imageFiles.map(f => f.file.name)
    const duplicateImages = imageNames.filter((name, index) => imageNames.indexOf(name) !== index)
    if (duplicateImages.length > 0) {
      errors.push(`Duplicate image filenames: ${duplicateImages.join(', ')}`)
    }

    return {
      isValid: errors.length === 0,
      errors,
      structure: {
        markdown: markdownFiles.length,
        images: imageFiles.length,
        total: files.length,
      },
    }
  }

  const getZipPreview = (files) => {
    const markdownFiles = files.filter(f => f.type === 'markdown')
    const imageFiles = files.filter(f => f.type === 'image')

    const structure = []

    // Add markdown file at root
    if (markdownFiles.length > 0) {
      structure.push({
        type: 'file',
        name: markdownFiles[0].file.name,
        path: markdownFiles[0].file.name,
        size: markdownFiles[0].file.size,
      })
    }

    // Add images folder if there are images
    if (imageFiles.length > 0) {
      structure.push({
        type: 'folder',
        name: 'images/',
        path: 'images/',
        children: imageFiles.map(f => ({
          type: 'file',
          name: f.file.name,
          path: `images/${f.file.name}`,
          size: f.file.size,
        })),
      })
    }

    return structure
  }

  return {
    createZip,
    validateZipStructure,
    getZipPreview,
  }
}
