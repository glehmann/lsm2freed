import itk, sys, os
# itk.auto_progress()

reader = itk.lsm()
writer = itk.ImageSeriesWriter.IUC3IUC2.New(reader)
names = itk.NumericSeriesFileNames.New()
names.SetStartIndex( 0 )

descriptorTpl = """
STACK "%(channelName)s";
IMAGESPATH "%(imagePath)s";
PIXWIDTH %(pixelWidth)s;
PIXHEIGHT %(pixelHeight)s;
RELPOSITION %(sliceSpacing)s;
"""

for f in sys.argv[1:] :
	print f,
	reader.SetFileName( f )
	names.SetEndIndex( itk.size( reader )[2] - 1 )
	lsmName = f[:-4]
	if not os.path.exists(lsmName ):
		os.mkdir( lsmName )
		
	descriptorDir = lsmName + "/sdf/"
	if not os.path.exists( descriptorDir ):
		os.mkdir( descriptorDir )
		
	for c in range( 0, reader.GetNumberOfChannels() ) :
		channelName = reader.SetChannel( c )
		print channelName,
		if not os.path.exists(lsmName + "/" + channelName ):
			os.mkdir( lsmName + "/" + channelName )
			
		spacing = itk.spacing( reader )
		descriptor = descriptorTpl % { "channelName": channelName,
						"imagePath": "../" + channelName,
						"pixelWidth": spacing[0],
						"pixelHeight": spacing[1],
						"sliceSpacing": spacing[2] }
		
		for s in range( 0, itk.size( reader )[2] ) :
			sName = str(s).zfill(3)
			descriptor += 'SLICE "' + sName + '" "' + sName + '.tif";\n'
		descriptorFile = file( descriptorDir + channelName + ".sdf", "w" )
		print >> descriptorFile, descriptor
		descriptorFile.close()
			
		nameFormat = lsmName + "/" + channelName + "/%03d.tif"
# 		print nameFormat
		names.SetSeriesFormat( nameFormat )
		writer.SetFileNames( names.GetFileNames() )
		writer.Update()
	print "done."
	