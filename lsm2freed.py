import itk, sys, os
# itk.auto_progress()

# the pipeline used to convert the lsm files to the a serie of tif used in freed
reader = itk.lsm()
writer = itk.ImageSeriesWriter.IUC3IUC2.New(reader)

# the names must be generated with a NumericSeriesFileNames object, because the 
# vector of strings are not usable yet from python
names = itk.NumericSeriesFileNames.New()
# make the slice number start at 0 instead of 1
names.SetStartIndex( 0 )

# the descriptor file contain a header...
descriptorHeaderTpl = """STACK "%(channelName)s";
IMAGESPATH "%(imagePath)s";
PIXWIDTH %(pixelWidth)s;
PIXHEIGHT %(pixelHeight)s;
RELPOSITION %(sliceSpacing)s;
"""
# and a line per slice
sliceDescriptorTpl = "SLICE %(sliceName)s %(fileName)s\n"

# lets convert all the files
for f in sys.argv[1:] :
	# display the file name, to know on what we are working
	print f,
	
	# change the file name
	reader.SetFileName( f )
	
	numberOfSlices = itk.size( reader )[2]
	spacing = itk.spacing( reader )
	
	lsmName = f[:-4]
	if not os.path.exists(lsmName ):
		os.mkdir( lsmName )
		
	descriptorDir = lsmName + "/sdf"
	if not os.path.exists( descriptorDir ):
		os.mkdir( descriptorDir )
		
	# set the number of slices for the name generator
	names.SetEndIndex( numberOfSlices - 1 )
	
	# now iterate over all the channel
	for c in range( 0, reader.GetNumberOfChannels() ) :
		channelName = reader.SetChannel( c )
		
		# again, print the channel name  to know what is done currently
		print channelName,
		
		channelDir = lsmName + "/" + channelName
		if not os.path.exists( channelDir ):
			os.mkdir( channelDir )
			
		descriptor = descriptorHeaderTpl % { "channelName": channelName,
						"imagePath": "../" + channelName,
						"pixelWidth": spacing[0],
						"pixelHeight": spacing[1],
						"sliceSpacing": spacing[2] }
		
		# fill the descriptor
		for s in range( 0, itk.size( reader )[2] ) :
			sName = str(s).zfill(3)
			descriptor += sliceDescriptorTpl % { "sliceName": sName, "fileName": sName + '.tif' }
		# and write the descriptor file to the disk
		descriptorFile = file( "%s/%s.sdf" % ( descriptorDir, channelName ), "w" )
		descriptorFile.write( descriptor )
		descriptorFile.close()
		
		# generate the file names for the writer
		nameFormat = "%s/%s/%%03d.tif" % ( lsmName, channelName )
# 		print nameFormat
		names.SetSeriesFormat( nameFormat )
		# and write the tif files
		writer.SetFileNames( names.GetFileNames() )
		writer.Update()
		
	print "done."
	